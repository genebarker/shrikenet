from datetime import datetime, timedelta, timezone
import logging

from shrikenet.entities.event import Event
from shrikenet.entities.event_tag import EventTag
from shrikenet.usecases.login_to_system_result import LoginToSystemResult


class LoginToSystem:

    USECASE_TAG = 'login_to_system'

    def __init__(self, services):
        self.db = services.storage_provider
        self.crypto = services.crypto_provider
        self.logger = logging.getLogger(__name__)

    def run(self, username, password, ip_address, new_password=None):
        try:
            self._verify_user_exists(username, ip_address)
            user = self.db.get_app_user_by_username(username)
            self._verify_user_active(user, ip_address)
            self._verify_user_unlocked(user, ip_address)
            self._verify_user_password_correct(user, password, ip_address)
            self._verify_user_password_reset_satisfied(user, new_password,
                                                       ip_address)
        except LoginToSystemError as error:
            return LoginToSystemResult(
                message=str(error),
                has_failed=True,
                must_change_password=error.must_change_password,
                )

        message = 'Login successful.'
        log_message = (f'App user (username={user.username}) from '
                       f'{ip_address} successfully logged in.')

        if new_password is not None:
            user.password_hash = self.crypto.generate_hash_from_string(
                new_password)
            user.needs_password_change = False
            suffix = ' Password successfully changed.'
            message += suffix
            log_message += suffix

        user.is_locked = False
        user.ongoing_password_failure_count = 0
        event = self._create_login_event(
            app_user_oid=user.oid,
            tag=EventTag.user_login,
            text=log_message
        )
        self.db.update_app_user(user)
        self.db.add_event(event)
        self.db.commit()
        self.logger.info(log_message)
        return LoginToSystemResult(message=message, has_failed=False,
                                   must_change_password=False,
                                   user_oid=user.oid)

    def _verify_user_exists(self, username, ip_address):
        if self.db.exists_app_username(username) is False:
            log_message = (f'Unknown app user (username={username}) from '
                           f'{ip_address} attempted to login.')
            self.logger.info(log_message)
            raise LoginToSystemError('Login attempt failed.')

    def _verify_user_active(self, user, ip_address):
        if user.is_dormant:
            log_message = (f'Dormant app user (username={user.username}) '
                           f'from {ip_address} attempted to login.')
            event = self._create_login_event(
                app_user_oid=user.oid,
                tag=EventTag.dormant_user,
                text=log_message
            )
            self.db.add_event(event)
            self.db.commit()
            self.logger.info(log_message)
            raise LoginToSystemError('Login attempt failed. Your '
                                     'credentials are invalid.')

    def _create_login_event(self, app_user_oid, tag, text):
        return Event(
            oid=self.db.get_next_event_oid(),
            time=datetime.now(timezone.utc),
            app_user_oid=app_user_oid,
            tag=tag,
            text=text,
            usecase_tag=self.USECASE_TAG,
        )

    def _verify_user_unlocked(self, user, ip_address):
        if self._lock_is_active(user):
            log_message = (f'Locked app user (username={user.username}) '
                           f'from {ip_address} attempted to login.')
            event = self._create_login_event(
                app_user_oid=user.oid,
                tag=EventTag.locked_user,
                text=log_message
            )
            self.db.add_event(event)
            self.db.commit()
            self.logger.info(log_message)
            raise LoginToSystemError('Login attempt failed. Your account '
                                     'is locked.')

    def _lock_is_active(self, user):
        if not user.is_locked:
            return False
        rules = self.db.get_rules()
        lock_length = timedelta(minutes=rules.login_fail_lock_minutes)
        lock_expire_time = user.last_password_failure_time + lock_length
        return datetime.now(timezone.utc) < lock_expire_time

    def _verify_user_password_correct(self, user, password, ip_address):
        if not self.crypto.hash_matches_string(user.password_hash, password):
            user.ongoing_password_failure_count += 1
            rules = self.db.get_rules()
            if (user.ongoing_password_failure_count >
                    rules.login_fail_threshold_count):
                user.is_locked = True
            user.last_password_failure_time = datetime.now(timezone.utc)
            self.db.update_app_user(user)
            self.db.commit()
            log_message = (f'App user (username={user.username}) from '
                           f'{ip_address} attempted to login with the '
                           f'wrong password (ongoing_password_failure_count='
                           f'{user.ongoing_password_failure_count}).')
            self.logger.info(log_message)
            raise LoginToSystemError('Login attempt failed.')

    def _verify_user_password_reset_satisfied(self, user, new_password,
                                              ip_address):
        if user.needs_password_change and new_password is None:
            log_message = (f'App user (username={user.username}) with '
                           f'password marked for reset from {ip_address} '
                           f'attempted to login without providing a new '
                           f'password.')
            event = self._create_login_event(
                app_user_oid=user.oid,
                tag=EventTag.must_change_password,
                text=log_message
            )
            self.db.add_event(event)
            self.db.commit()
            self.logger.info(log_message)
            raise LoginToSystemError('Password marked for reset. Must '
                                     'supply a new password.',
                                     must_change_password=True)


class LoginToSystemError(Exception):
    def __init__(self, message, must_change_password=False):
        super().__init__(message)
        self.must_change_password = must_change_password
