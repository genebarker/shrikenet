import copy
from datetime import datetime, timezone

import pytest

from shrikenet.entities.app_user import AppUser
from shrikenet.entities.event import Event
from shrikenet.entities.exceptions import (
    DatastoreError,
    DatastoreKeyError,
)


CHRISTMAS_2018 = datetime(2018, 12, 25, 0, 0, tzinfo=timezone.utc)


# pylint: disable=redefined-outer-name
@pytest.fixture
def existing_event(db):
    user = AppUser(
        oid=88,
        username='fmulder',
        name='Fox Mulder',
        password_hash=None,
    )
    db.add_app_user(user)
    event = Event(
        oid=1234,
        time=CHRISTMAS_2018,
        app_user_oid=88,
        tag='password_failure',
        text='fmulder entered wrong password.',
        usecase_tag='login_user',
        app_user_name='Fox Mulder',
    )
    db.add_event(event)
    return event


def test_get_by_oid_gets_record(db, existing_event):
    stored_event = db.get_event_by_oid(existing_event.oid)
    assert stored_event == existing_event


def test_get_by_oid_gets_a_copy(db, existing_event):
    existing_event.text = 'Different'
    stored_event = db.get_event_by_oid(existing_event.oid)
    assert stored_event != existing_event


def test_get_by_oid_unknown_raises(db):
    regex = 'can not get event .oid=12345., reason: '
    with pytest.raises(DatastoreKeyError, match=regex):
        db.get_event_by_oid(12345)


def test_add_event_adds_record(db, existing_event):
    stored_event = db.get_event_by_oid(existing_event.oid)
    assert stored_event == existing_event


def test_add_event_adds_a_copy(db, existing_event):
    existing_event.text = 'Different'
    stored_event = db.get_event_by_oid(existing_event.oid)
    assert stored_event != existing_event


def test_add_event_with_duplicate_oid_raises(db, existing_event):
    new_event = copy.copy(existing_event)
    new_event.text = 'Different'
    regex = ('can not add event .oid={}, tag={}., reason: '
             .format(existing_event.oid, existing_event.tag))
    with pytest.raises(DatastoreError, match=regex):
        db.add_event(new_event)
