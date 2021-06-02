from datetime import datetime, timezone

from shrikenet.entities.log_entry import LogEntry


CHRISTMAS_2018 = datetime(2018, 12, 25, 0, 0, tzinfo=timezone.utc)


def test_base_field_initialization():
    log_entry = create_good_log_entry()
    assert log_entry.oid == 2112
    assert log_entry.time == CHRISTMAS_2018
    assert log_entry.app_user_oid == 123
    assert log_entry.tag == 'duck_found'
    assert log_entry.text == 'fmulder found a duck.'
    assert log_entry.usecase_tag == 'look_for_duck'
    assert log_entry.app_user_name is None


def create_good_log_entry():
    return LogEntry(
        oid=2112,
        time=CHRISTMAS_2018,
        app_user_oid=123,
        tag='duck_found',
        text='fmulder found a duck.',
        usecase_tag='look_for_duck',
    )


def test_optional_field_initialization():
    log_entry = LogEntry(
        oid=None,
        time=None,
        app_user_oid=None,
        tag=None,
        text=None,
        usecase_tag=None,
        app_user_name='Fox Mulder'
    )
    assert log_entry.app_user_name == 'Fox Mulder'
