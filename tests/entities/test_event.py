from datetime import datetime, timezone

import pytest

from shrikenet.entities.event import Event


CHRISTMAS_2018 = datetime(2018, 12, 25, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_event():
    return Event(
        time=CHRISTMAS_2018,
        app_user_oid=123,
        tag='duck_found',
        text='fmulder found a duck.',
        usecase_tag='look_for_duck',
    )


def test_minimal_initialization(sample_event):
    assert sample_event.time == CHRISTMAS_2018
    assert sample_event.app_user_oid == 123
    assert sample_event.tag == 'duck_found'
    assert sample_event.text == 'fmulder found a duck.'
    assert sample_event.usecase_tag == 'look_for_duck'
