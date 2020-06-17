import pytest

from shrikenet.entities.event_validator import EventValidator
from shrikenet.entities.record_validator import RecordValidator


def test_is_a_record_validator():
    assert issubclass(EventValidator, RecordValidator)
