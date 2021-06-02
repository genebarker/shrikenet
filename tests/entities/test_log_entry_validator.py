import pytest

from shrikenet.adapters.memory import Memory
from shrikenet.entities.app_user import AppUser
from shrikenet.entities.log_entry_validator import LogEntryValidator
from shrikenet.entities.record_validator import RecordValidator

from tests.entities.test_log_entry import create_good_log_entry


# pylint: disable=redefined-outer-name
@pytest.fixture
def log_entry():
    return create_good_log_entry()


def test_is_a_record_validator():
    assert issubclass(LogEntryValidator, RecordValidator)


def test_successful_validation_returns_none(log_entry):
    assert LogEntryValidator.validate_fields(log_entry) is None


def test_oid_required(log_entry):
    log_entry.oid = None
    verify_validation_raises(log_entry)


def verify_validation_raises(log_entry):
    with pytest.raises(ValueError):
        LogEntryValidator.validate_fields(log_entry)


def test_oid_validated(log_entry):
    log_entry.oid = 'bad'
    verify_validation_raises(log_entry)


def test_time_required(log_entry):
    log_entry.time = None
    verify_validation_raises(log_entry)


def test_time_validated(log_entry):
    log_entry.time = 123
    verify_validation_raises(log_entry)


def test_app_user_id_required(log_entry):
    log_entry.app_user_oid = None
    verify_validation_raises(log_entry)


def test_app_user_id_validated(log_entry):
    log_entry.app_user_oid = 'bad'
    verify_validation_raises(log_entry)


def test_tag_required(log_entry):
    log_entry.tag = None
    verify_validation_raises(log_entry)


def test_tag_validated(log_entry):
    log_entry.tag = 'Bad tag'
    verify_validation_raises(log_entry)


def test_usecase_tag_required(log_entry):
    log_entry.usecase_tag = None
    verify_validation_raises(log_entry)


def test_usecase_tag_validated(log_entry):
    log_entry.usecase_tag = 'Bad tag'
    verify_validation_raises(log_entry)


def test_text_required(log_entry):
    log_entry.text = None
    verify_validation_raises(log_entry)


def test_text_validated(log_entry):
    log_entry.text = 'a' * (LogEntryValidator.text_max_length + 1)
    verify_validation_raises(log_entry)


@pytest.fixture
def db():
    provider = Memory()
    provider.open()
    yield provider
    provider.close()


def test_unknown_app_user_oid_raises(log_entry, db):
    with pytest.raises(Exception) as excinfo:
        LogEntryValidator.validate_references(log_entry, db)

    expected_message = (
        'can not get app_user (oid={}), reason: '
        .format(log_entry.app_user_oid)
    )
    assert expected_message in str(excinfo.value)


def test_known_app_user_validates(log_entry, db):
    user = AppUser(log_entry.app_user_oid, None, log_entry.app_user_name, None)
    db.add_app_user(user)
    assert LogEntryValidator.validate_references(log_entry, db) is None
