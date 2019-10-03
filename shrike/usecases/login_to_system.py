from shrike.usecases.login_to_system_output import LoginToSystemOutput


class LoginToSystem:

    @staticmethod
    def execute(input):
        storage_provider = input.services.storage_provider
        crypto_provider = input.services.crypto_provider

        if storage_provider.exists_app_username(input.username) is False:
            return LoginToSystemOutput(False)

        user = storage_provider.get_app_user_by_username(input.username)
        if crypto_provider.hash_matches_string(user.password_hash, input.password):
            return LoginToSystemOutput(True)

        return LoginToSystemOutput(False)
