import pytest

from shrike.entities.exceptions import ShrikeException


class TestShrikeException:

    def test_sets_message(self):
        with pytest.raises(ShrikeException) as excinfo:
            raise ShrikeException('some message')

        assert excinfo.value.message == 'some message'

    def test_has_default_message(self):
        with pytest.raises(ShrikeException) as excinfo:
            raise ShrikeException()

        assert excinfo.value.message == 'an unexpected error occurred'
