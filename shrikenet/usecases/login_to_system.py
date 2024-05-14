from datetime import datetime, timedelta
import logging

from shrikenet.entities.log_entry import LogEntry
from shrikenet.entities.log_entry_tag import LogEntryTag
from shrikenet.usecases.login_to_system_result import LoginToSystemResult


class LoginToSystem:

    USECASE_TAG = "login_to_system"

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
            self._verify_user_password_reset_satisfied(
                user, new_password, ip_address
            )
            if new_password is not None:
                self._verify_password_is_different(
                    user, ip_address, password, new_password
                )

        except LoginToSystemError as error:
            return LoginToSystemResult(
                message=str(error),
                has_failed=True,
                must_change_password=error.must_change_password,
            )

        message = "Login successful."
        log_entry_text = (
            f"App user (username={user.username}) from "
            f"{ip_address} successfully logged in."
        )

        if new_password is not None:
            user.password_hash = self.crypto.generate_hash_from_string(
                new_password
            )
            user.needs_password_change = False
            suffix = " Password successfully changed."
            message += suffix
            log_entry_text += suffix

        user.is_locked = False
        user.ongoing_password_failure_count = 0
        self.db.update_app_user(user)
        log_entry_tag = LogEntryTag.user_login
        self._record_log_entry(user.oid, log_entry_tag, log_entry_text)
        return LoginToSystemResult(
            message=message,
            has_failed=False,
            must_change_password=False,
            user_oid=user.oid,
        )

    def _verify_user_exists(self, username, ip_address):
        if self.db.exists_app_username(username) is False:
            log_entry_tag = LogEntryTag.unknown_user
            log_entry_text = (
                f"Unknown app user (username={username}) "
                f"from {ip_address} attempted to login."
            )
            self._record_log_entry(None, log_entry_tag, log_entry_text)
            raise LoginToSystemError("Login attempt failed.")

    def _record_log_entry(self, app_user_oid, tag, text):
        log_entry = self._create_login_log_entry(app_user_oid, tag, text)
        log_entry.oid = self.db.add_log_entry(log_entry)
        self.logger.info(text)
        self.db.commit()

    def _create_login_log_entry(self, app_user_oid, log_entry_tag, text):
        return LogEntry(
            -1,
            datetime.now(),
            app_user_oid,
            log_entry_tag,
            text,
            self.USECASE_TAG,
        )

    def _verify_user_active(self, user, ip_address):
        if user.is_dormant:
            log_entry_tag = LogEntryTag.dormant_user
            log_entry_text = (
                f"Dormant app user (username={user.username}) "
                f"from {ip_address} attempted to login."
            )
            self._record_log_entry(user.oid, log_entry_tag, log_entry_text)
            raise LoginToSystemError(
                "Login attempt failed. Your credentials are invalid."
            )

    def _verify_user_unlocked(self, user, ip_address):
        if self._lock_is_active(user):
            log_entry_tag = LogEntryTag.locked_user
            log_entry_text = (
                f"Locked app user (username={user.username}) "
                f"from {ip_address} attempted to login."
            )
            self._record_log_entry(user.oid, log_entry_tag, log_entry_text)
            raise LoginToSystemError(
                "Login attempt failed. Your account is locked."
            )

    def _lock_is_active(self, user):
        if not user.is_locked:
            return False
        rules = self.db.get_rules()
        lock_length = timedelta(minutes=rules.login_fail_lock_minutes)
        lock_expire_time = user.last_password_failure_time + lock_length
        return datetime.now() < lock_expire_time

    def _verify_user_password_correct(self, user, password, ip_address):
        if not self.crypto.hash_matches_string(
            user.password_hash, password
        ):
            user.ongoing_password_failure_count += 1
            rules = self.db.get_rules()
            if (
                user.ongoing_password_failure_count
                > rules.login_fail_threshold_count
            ):
                user.is_locked = True
            user.last_password_failure_time = datetime.now()
            self.db.update_app_user(user)
            log_entry_tag = LogEntryTag.wrong_password
            log_entry_text = (
                f"App user (username={user.username}) from {ip_address} "
                f"attempted to login with the wrong password "
                f"(ongoing_password_failure_count="
                f"{user.ongoing_password_failure_count})."
            )
            self._record_log_entry(user.oid, log_entry_tag, log_entry_text)
            raise LoginToSystemError("Login attempt failed.")

    def _verify_user_password_reset_satisfied(
        self, user, new_password, ip_address
    ):
        if user.needs_password_change and new_password is None:
            log_entry_tag = LogEntryTag.must_change_password
            log_entry_text = (
                f"App user (username={user.username}) with password marked "
                f"for reset from {ip_address} attempted to login without "
                f"providing a new password."
            )
            self._record_log_entry(user.oid, log_entry_tag, log_entry_text)
            raise LoginToSystemError(
                "Password marked for reset. Must supply a new password.",
                must_change_password=True,
            )

    def _verify_password_is_different(
        self, user, ip_address, old_password, new_password
    ):
        if old_password != new_password:
            return
        log_entry_tag = LogEntryTag.unfit_password
        log_entry_text = (
            f"App user (username={user.username}) from {ip_address} "
            f"attempted to login with a password change but the new "
            f"password was the same as the current one."
        )
        self._record_log_entry(user.oid, log_entry_tag, log_entry_text)
        raise LoginToSystemError(
            "Password change failed. New password can not be the same as "
            "the current one."
        )


class LoginToSystemError(Exception):
    def __init__(self, message, must_change_password=False):
        super().__init__(message)
        self.must_change_password = must_change_password
