from shrike.usecases.login_to_system_result import LoginToSystemResult


class LoginToSystem:

    def __init__(self, services):
        self.services = services

    def run(self, username, password, new_password=None):
        try:
            self._verify_user_exists(username)
            db = self.services.storage_provider
            user = db.get_app_user_by_username(username)
            self._verify_user_password_correct(user, password)
            self._verify_user_unlocked(user)
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

        db.commit()
        return LoginToSystemResult(message=message, has_failed=False)

    def _verify_user_exists(self, username):
        db = self.services.storage_provider
        if db.exists_app_username(username) is False:
            raise LoginToSystemError('Login attempt failed.')

    def _verify_user_password_correct(self, user, password):
        crypto = self.services.crypto_provider
        if not crypto.hash_matches_string(user.password_hash, password):
            raise LoginToSystemError('Login attempt failed.')

    def _verify_user_unlocked(self, user):
        if user.is_locked:
            raise LoginToSystemError('Login attempt failed. Your account '
                                     'is locked.')

    def _verify_user_password_reset_satisfied(self, user, new_password):
        if new_password is not None:
            return

        if user.needs_password_change:
            raise LoginToSystemError('Password marked for reset. Must '
                                     'supply a new password.',
                                     must_change_password=True)

    def _update_user_password(self, user, new_password):
        crypto = self.services.crypto_provider
        user.password_hash = crypto.generate_hash_from_string(new_password)
        db = self.services.storage_provider
        db.update_app_user(user)


class LoginToSystemError(Exception):
    def __init__(self, message, must_change_password=False):
        self.message = message
        self.must_change_password = must_change_password
