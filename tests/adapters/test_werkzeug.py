import pytest

from shrikenet.adapters.werkzeug import Werkzeug
from tests.adapters.test_swapcase import TestSwapcase


class TestWerkzeug(TestSwapcase):

    TEST_STRING = "scully"
    HASH_OF_TEST_STRING = (
        "pbkdf2:sha256:150000$zS5INwXP$"
        "928b443301f6ffff372d56a517fb56af2670470c26dfcb631777e58353c78294"
    )
    WRONG_HASH = (
        "pbkdf2:sha256:150000$WMjtL3IB$"
        "77df11f2d56a97fde77db9a2a7fee3d1c24cffc94c2f76bb4ef9d162d864c1b5"
    )

    @staticmethod
    def get_crypto_provider():
        return Werkzeug()
