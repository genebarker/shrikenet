import pytest

from shrikenet.entities.event_validator import EventValidator
from shrikenet.entities.record_validator import RecordValidator

from tests.entities.test_event import create_good_event


def test_is_a_record_validator():
    assert issubclass(EventValidator, RecordValidator)


def test_successful_validation_returns_none():
    event = create_good_event()
    assert EventValidator.validate_fields(event) is None


def test_oid_required():
    event = create_good_event()
    event.oid = None
    verify_validation_raises(event)


def verify_validation_raises(event):
    with pytest.raises(ValueError):
        EventValidator.validate_fields(event)

def test_time_required():
    event = create_good_event()
    event.time = None
    verify_validation_raises(event)

def test_time_validated():
    event = create_good_event()
    event.time = 123
    verify_validation_raises(event)
