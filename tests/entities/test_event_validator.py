import pytest

from shrikenet.entities.event_validator import EventValidator
from shrikenet.entities.record_validator import RecordValidator

from tests.entities.test_event import create_good_event


# pylint: disable=redefined-outer-name
@pytest.fixture
def event():
    return create_good_event()


def test_is_a_record_validator():
    assert issubclass(EventValidator, RecordValidator)


def test_successful_validation_returns_none(event):
    assert EventValidator.validate_fields(event) is None


def test_oid_required(event):
    event.oid = None
    verify_validation_raises(event)


def verify_validation_raises(event):
    with pytest.raises(ValueError):
        EventValidator.validate_fields(event)


def test_oid_validated(event):
    event.oid = 'bad'
    verify_validation_raises(event)


def test_time_required(event):
    event.time = None
    verify_validation_raises(event)


def test_time_validated(event):
    event.time = 123
    verify_validation_raises(event)


def test_app_user_id_required(event):
    event.app_user_oid = None
    verify_validation_raises(event)


def test_app_user_id_validated(event):
    event.app_user_oid = 'bad'
    verify_validation_raises(event)


def test_tag_required(event):
    event.tag = None
    verify_validation_raises(event)


def test_tag_validated(event):
    event.tag = 'Bad tag'
    verify_validation_raises(event)


def test_usecase_tag_required(event):
    event.usecase_tag = None
    verify_validation_raises(event)


def test_usecase_tag_validated(event):
    event.usecase_tag = 'Bad tag'
    verify_validation_raises(event)


def test_text_required(event):
    event.text = None
    verify_validation_raises(event)


def test_text_validated(event):
    event.text = 'a' * (EventValidator.text_max_length + 1)
    verify_validation_raises(event)
