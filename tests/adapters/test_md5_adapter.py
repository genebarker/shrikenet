import pytest

from shrike.adapters.md5_adapter import MD5Adapter
from shrike.entities.crypto_provider import CryptoProvider

class TestMD5Adapter:

    TEST_STRING = 'scully'
    HASH_OF_TEST_STRING = 'a3aab32ace277bdf141f92c1e68f6cef'
    
    @staticmethod
    def get_crypto_provider():
        return MD5Adapter()

    @pytest.fixture
    def crypto_provider(self):
        return self.get_crypto_provider()

    def test_is_a_crypto_provider(self, crypto_provider):
        assert isinstance(crypto_provider, CryptoProvider)

    def test_generates_correct_hash_for_string(self, crypto_provider):
        assert crypto_provider.generate_hash_from_string(self.TEST_STRING) == self.HASH_OF_TEST_STRING

    def test_when_hash_matches_string(self, crypto_provider):
        assert crypto_provider.hash_matches_string(self.HASH_OF_TEST_STRING, self.TEST_STRING)

    @pytest.mark.parametrize(('my_hash', 'my_string'), (
        ('a', 'b'),
        (None, 'b'),
        ('a', None),
        (None, None),
    ))
    def test_when_hash_does_not_match_string(self, crypto_provider, my_hash, my_string):
        assert crypto_provider.hash_matches_string(my_hash, my_string) is False
