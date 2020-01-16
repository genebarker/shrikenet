from datetime import datetime, timedelta, timezone
import logging

from shrike.entities.constants import Constants
from shrike.usecases.login_to_system_result import LoginToSystemResult


class LoginToSystem:

    def __init__(self, services):
        self.db = services.storage_provider
        self.crypto = services.crypto_provider
        self.logger = logging.getLogger(__name__)

    def run(self, username, password, ip_address, new_password=None):
        try:
            self._verify_user_exists(username, ip_address)
            user = self.db.get_app_user_by_username(username)
            self._verify_user_active(user)
            self._verify_user_unlocked(user)
            self._verify_user_password_correct(user, password, ip_address)
            self._verify_user_password_reset_satisfied(user, new_password)
        except LoginToSystemError as e:
            return LoginToSystemResult(
                message=e.message,
                has_failed=True,
                must_change_password=e.must_change_password,
                )

        message = 'Login successful.'

        if new_password is not None:
            user.password_hash = self.crypto.generate_hash_from_string(
                new_password)
            message = message + ' Password successfully changed.'

        user.is_locked = False
        user.ongoing_password_failure_count = 0
        self.db.update_app_user(user)
        self.db.commit()
        self.logger.info('App user (username=%s) from %s successfully '
                         'logged in.', user.username, ip_address)
        return LoginToSystemResult(message=message, has_failed=False,
                                   must_change_password=False,
                                   user_oid=user.oid)

    def _verify_user_exists(self, username, ip_address):
        if self.db.exists_app_username(username) is False:
            self.logger.info('Unknown app user (username=%s) from %s '
                             'attempted to login.', username, ip_address)
            raise LoginToSystemError('Login attempt failed.')

    def _verify_user_password_correct(self, user, password, ip_address):
        if not self.crypto.hash_matches_string(user.password_hash, password):
            user.ongoing_password_failure_count += 1
            if (user.ongoing_password_failure_count >
                    Constants.LOGIN_FAIL_THRESHOLD_COUNT):
                user.is_locked = True
            user.last_password_failure_time = datetime.now(timezone.utc)
            self.db.update_app_user(user)
            self.db.commit()
            self.logger.info('App user (username=%s) from %s attempted to '
                             'login with the wrong password '
                             '(ongoing_password_failure_count=%s).',
                             user.username, ip_address,
                             user.ongoing_password_failure_count)
            raise LoginToSystemError('Login attempt failed.')

    def _verify_user_active(self, user):
        if user.is_dormant:
            raise LoginToSystemError('Login attempt failed. Your '
                                     'credentials are invalid.')

    def _verify_user_unlocked(self, user):
        if self._lock_is_active(user):
            raise LoginToSystemError('Login attempt failed. Your account '
                                     'is locked.')

    def _lock_is_active(self, user):
        if not user.is_locked:
            return False
        lock_length = timedelta(minutes=Constants.LOGIN_FAIL_LOCK_MINUTES)
        lock_expire_time = user.last_password_failure_time + lock_length
        return datetime.now(timezone.utc) < lock_expire_time

    def _verify_user_password_reset_satisfied(self, user, new_password):
        if user.needs_password_change and new_password is None:
            raise LoginToSystemError('Password marked for reset. Must '
                                     'supply a new password.',
                                     must_change_password=True)


class LoginToSystemError(Exception):
    def __init__(self, message, must_change_password=False):
        self.message = message
        self.must_change_password = must_change_password
