import pytest

from shrike.entities.exceptions import ShrikeException


class TestShrikeException:

    def test_sets_message(self):
        with pytest.raises(ShrikeException) as excinfo:
            raise ShrikeException('some message')

        assert str(excinfo.value) == 'some message'

    def test_has_default_message(self):
        with pytest.raises(ShrikeException) as excinfo:
            raise ShrikeException()

        assert str(excinfo.value) == 'an unexpected error occurred'
