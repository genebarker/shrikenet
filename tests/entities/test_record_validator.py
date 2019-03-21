from shrike.entities.record_validator import RecordValidator


def test_placeholder_for_validate_fields():
    the_object = "Some object"
    assert RecordValidator.validate_fields(the_object) is None

def test_placeholder_for_validate_references():
    the_object = "Some object"
    storage_provider = None
    assert RecordValidator.validate_references(the_object, storage_provider) is None
