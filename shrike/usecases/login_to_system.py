from shrike.usecases.login_to_system_result import LoginToSystemResult


class LoginToSystem:

    def __init__(self, services, presenter):
        self.services = services
        self.presenter = presenter

    def run(self, username, password):
        storage_provider = self.services.storage_provider
        crypto_provider = self.services.crypto_provider

        if storage_provider.exists_app_username(username) is False:
            result = LoginToSystemResult('Login attempt failed.')
            self.presenter.present(result)
            return result

        user = storage_provider.get_app_user_by_username(username)
        if crypto_provider.hash_matches_string(
                user.password_hash, password) is False:
            result = LoginToSystemResult('Login attempt failed.')
            self.presenter.present(result)
            return result

        if user.needs_password_change:
            result = LoginToSystemResult('Password marked for reset. Must '
                                         'supply new_password.')
            result.must_change_password = True
            self.presenter.present(result)
            return result

        result = LoginToSystemResult('Login successful.',
                                     was_successful=True)
        self.presenter.present(result)
        return result
