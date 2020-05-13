import importlib

import pytest

from shrikenet.entities.exceptions import ShrikeException, DatastoreKeyError


class TestShrikeException:

    def test_sets_message(self):
        with pytest.raises(ShrikeException) as excinfo:
            raise ShrikeException('some message')

        assert str(excinfo.value) == 'some message'

    def test_has_default_message(self):
        with pytest.raises(ShrikeException) as excinfo:
            raise ShrikeException()

        assert str(excinfo.value) == 'an unexpected error occurred'

    @pytest.mark.parametrize(('exception_name',), (
        ('DatastoreClosed',),
        ('DatastoreAlreadyOpen',),
        ('DatastoreError',),
        ('DatastoreKeyError',),
    ))
    def test_exception_is_shrike_exception(self, exception_name):
        module = importlib.import_module('shrikenet.entities.exceptions')
        exception_class = getattr(module, exception_name)
        with pytest.raises(exception_class) as excinfo:
            raise exception_class()

        assert isinstance(excinfo.value, ShrikeException)

    def test_datastore_key_error_is_a_key_error(self):
        with pytest.raises(DatastoreKeyError) as excinfo:
            raise DatastoreKeyError()

        assert isinstance(excinfo.value, KeyError)
