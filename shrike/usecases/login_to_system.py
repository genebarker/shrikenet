from datetime import datetime, timezone

from shrike.usecases.login_to_system_result import LoginToSystemResult


class LoginToSystem:

    def __init__(self, services):
        self.db = services.storage_provider
        self.crypto = services.crypto_provider

    def run(self, username, password, new_password=None):
        try:
            self._verify_user_exists(username)
            user = self.db.get_app_user_by_username(username)
            self._verify_user_password_correct(user, password)
            self._verify_user_unlocked(user)
            self._verify_user_active(user)
            self._verify_user_password_reset_satisfied(user, new_password)
        except LoginToSystemError as e:
            return LoginToSystemResult(
                message=e.message,
                has_failed=True,
                must_change_password=e.must_change_password,
                )

        message = 'Login successful.'

        if new_password is not None:
            self._update_user_password(user, new_password)
            message = message + ' Password successfully changed.'

        user.ongoing_password_failure_count = 0
        self.db.update_app_user(user)
        self.db.commit()
        return LoginToSystemResult(message=message, has_failed=False)

    def _verify_user_exists(self, username):
        if self.db.exists_app_username(username) is False:
            raise LoginToSystemError('Login attempt failed.')

    def _verify_user_password_correct(self, user, password):
        if not self.crypto.hash_matches_string(user.password_hash, password):
            user.ongoing_password_failure_count += 1
            user.last_password_failure_time = datetime.now(timezone.utc)
            self.db.update_app_user(user)
            self.db.commit()
            raise LoginToSystemError('Login attempt failed.')

    def _verify_user_active(self, user):
        if user.is_dormant:
            raise LoginToSystemError('Login attempt failed. Your '
                                     'credentials are invalid.')

    def _verify_user_unlocked(self, user):
        if user.is_locked:
            raise LoginToSystemError('Login attempt failed. Your account '
                                     'is locked.')

    def _verify_user_password_reset_satisfied(self, user, new_password):
        if user.needs_password_change and new_password is None:
            raise LoginToSystemError('Password marked for reset. Must '
                                     'supply a new password.',
                                     must_change_password=True)

    def _update_user_password(self, user, new_password):
        user.password_hash = self.crypto.generate_hash_from_string(
            new_password)
        self.db.update_app_user(user)


class LoginToSystemError(Exception):
    def __init__(self, message, must_change_password=False):
        self.message = message
        self.must_change_password = must_change_password
