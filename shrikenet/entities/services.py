class Services:

    def __init__(
        self,
        storage_provider=None,
        text_transformer=None,
        crypto_provider=None,
        password_checker=None,
    ):
        self.storage_provider = storage_provider
        self.text_transformer = text_transformer
        self.crypto_provider = crypto_provider
        self.password_checker = password_checker
