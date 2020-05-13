import pytest

from shrikenet.entities.record_validator import RecordValidator


def test_validate_fields_uncallable():
    with pytest.raises(NotImplementedError):
        the_object = 'Some object'
        RecordValidator.validate_fields(the_object)


def test_validate_references_uncallable():
    with pytest.raises(NotImplementedError):
        the_object = 'Some object'
        storage_provider = None
        RecordValidator.validate_references(the_object, storage_provider)
