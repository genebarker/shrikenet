from shrike.usecases.login_to_system_result import LoginToSystemResult


class LoginToSystem:

    def __init__(self, services):
        self.services = services

    def run(self, username, password, new_password=None):
        storage_provider = self.services.storage_provider
        crypto_provider = self.services.crypto_provider

        if storage_provider.exists_app_username(username) is False:
            result = LoginToSystemResult('Login attempt failed.')
            return result

        user = storage_provider.get_app_user_by_username(username)
        if crypto_provider.hash_matches_string(
                user.password_hash, password) is False:
            result = LoginToSystemResult('Login attempt failed.')
            return result

        if user.is_locked:
            result = LoginToSystemResult('Login attempt failed. User is '
                                         'locked.')
            return result

        if user.needs_password_change:
            result = LoginToSystemResult('Password marked for reset. Must '
                                         'supply new_password.')
            result.must_change_password = True
            return result

        if new_password is not None:
            user.password_hash = crypto_provider.generate_hash_from_string(
                new_password)
            storage_provider.update_app_user(user)
            storage_provider.commit()
            result = LoginToSystemResult('Password successfully changed.',
                                         has_failed=False)
            return result

        result = LoginToSystemResult('Login successful.', has_failed=False)
        return result
