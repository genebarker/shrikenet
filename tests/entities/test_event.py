from datetime import datetime, timezone

import pytest

from shrikenet.entities.event import Event


CHRISTMAS_2018 = datetime(2018, 12, 25, 0, 0, tzinfo=timezone.utc)


def test_base_field_initialization():
    e = Event(
        oid=2112,
        time=CHRISTMAS_2018,
        app_user_oid=123,
        tag='duck_found',
        text='fmulder found a duck.',
        usecase_tag='look_for_duck',
    )
    assert e.oid == 2112
    assert e.time == CHRISTMAS_2018
    assert e.app_user_oid == 123
    assert e.tag == 'duck_found'
    assert e.text == 'fmulder found a duck.'
    assert e.usecase_tag == 'look_for_duck'
    assert e.app_user_name is None

def test_optional_field_initialization():
    e = Event(
        oid=None,
        time=None,
        app_user_oid=None,
        tag=None,
        text=None,
        usecase_tag=None,
        app_user_name='Fox Mulder'
    )
    assert e.app_user_name == 'Fox Mulder'
