from datetime import datetime, timezone

import pytest

from shrikenet.entities.event import Event


CHRISTMAS_2018 = datetime(2018, 12, 25, 0, 0, tzinfo=timezone.utc)


def test_base_field_initialization():
    event = create_good_event()
    assert event.oid == 2112
    assert event.time == CHRISTMAS_2018
    assert event.app_user_oid == 123
    assert event.tag == 'duck_found'
    assert event.text == 'fmulder found a duck.'
    assert event.usecase_tag == 'look_for_duck'
    assert event.app_user_name is None


def create_good_event():
    return Event(
        oid=2112,
        time=CHRISTMAS_2018,
        app_user_oid=123,
        tag='duck_found',
        text='fmulder found a duck.',
        usecase_tag='look_for_duck',
    )


def test_optional_field_initialization():
    event = Event(
        oid=None,
        time=None,
        app_user_oid=None,
        tag=None,
        text=None,
        usecase_tag=None,
        app_user_name='Fox Mulder'
    )
    assert event.app_user_name == 'Fox Mulder'
