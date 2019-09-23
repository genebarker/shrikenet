import pytest

from shrike.adapters.md5_adapter import MD5Adapter
from shrike.entities.crypto_provider import CryptoProvider

class TestMD5Adapter:

    @staticmethod
    def get_crypto_provider():
        return MD5Adapter()

    @pytest.fixture
    def crypto_provider(self):
        return self.get_crypto_provider()

    def test_is_a_crypto_provider(self, crypto_provider):
        assert isinstance(crypto_provider, CryptoProvider)
