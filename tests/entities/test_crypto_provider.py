import pytest

from shrike.entities.crypto_provider import CryptoProvider

class TestCryptoProvider:

    def test_interface_cant_be_instantiated(self):
        with pytest.raises(NotImplementedError):
            CryptoProvider()

    @pytest.fixture
    def crypto_adapter(self):
        class FakeAdapter(CryptoProvider):
            def __init__(self):
                pass
        return FakeAdapter()

    def test_generate_hash_method_cant_be_called(self, crypto_adapter):
        with pytest.raises(NotImplementedError):
            crypto_adapter.generate_hash_from_string('a')

    def test_hash_matches_string_cant_be_called(self, crypto_adapter):
        with pytest.raises(NotImplementedError):
            crypto_adapter.hash_matches_string('a', 'b')
