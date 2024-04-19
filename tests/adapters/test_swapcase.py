import pytest

from shrikenet.adapters.swapcase import Swapcase
from shrikenet.entities.crypto_provider import CryptoProvider


class TestSwapcase:

    TEST_STRING = "scully"
    HASH_OF_TEST_STRING = "SCULLY"
    WRONG_HASH = "Mulder"

    @staticmethod
    def get_crypto_provider():
        return Swapcase()

    @pytest.fixture
    def crypto_provider(self):
        return self.get_crypto_provider()

    def test_is_a_crypto_provider(self, crypto_provider):
        assert isinstance(crypto_provider, CryptoProvider)

    def test_generates_hash_for_string(self, crypto_provider):
        hash_ = crypto_provider.generate_hash_from_string(self.TEST_STRING)
        assert len(hash_) > 0
        assert hash_ != self.TEST_STRING

    def test_when_hash_matches_string(self, crypto_provider):
        assert crypto_provider.hash_matches_string(
            self.HASH_OF_TEST_STRING, self.TEST_STRING
        )

    @pytest.mark.parametrize(
        ("my_hash", "my_string"),
        (
            (WRONG_HASH, TEST_STRING),
            (WRONG_HASH, None),
            (None, TEST_STRING),
            (None, None),
        ),
    )
    def test_when_hash_does_not_match_string(
        self, crypto_provider, my_hash, my_string
    ):
        assert (
            crypto_provider.hash_matches_string(my_hash, my_string) is False
        )
