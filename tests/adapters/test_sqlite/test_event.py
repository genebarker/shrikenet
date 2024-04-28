import copy
from datetime import datetime

import pytest

from shrikenet.adapters.sqlite import SQLite
from shrikenet.entities.app_user import AppUser
from shrikenet.entities.log_entry import LogEntry
from shrikenet.entities.exceptions import (
    DatastoreKeyError,
)

DATABASE = "test.db"


CHRISTMAS_2018 = datetime(2018, 12, 25, 0, 0)


@pytest.fixture
def db():
    database = SQLite(DATABASE)
    database.open()
    database.build_database_schema()
    yield database
    database.close()


@pytest.fixture
def existing_log_entry(db):
    user = AppUser(
        oid=-1,
        username="fmulder",
        name="Fox Mulder",
        password_hash=None,
    )
    user.oid = db.add_app_user(user)
    log_entry = LogEntry(
        oid=-1,
        time=CHRISTMAS_2018,
        app_user_oid=user.oid,
        tag="password_failure",
        text="fmulder entered wrong password.",
        usecase_tag="login_user",
        app_user_name="Fox Mulder",
    )
    log_entry.oid = db.add_log_entry(log_entry)
    return log_entry


def test_get_by_oid_gets_record(db, existing_log_entry):
    stored_log_entry = db.get_log_entry_by_oid(existing_log_entry.oid)
    assert stored_log_entry == existing_log_entry


def test_get_by_oid_unknown_raises(db):
    regex = "can not get log entry .oid=12345., reason: "
    with pytest.raises(DatastoreKeyError, match=regex):
        db.get_log_entry_by_oid(12345)


def test_add_log_entry_adds_record(db, existing_log_entry):
    stored_log_entry = db.get_log_entry_by_oid(existing_log_entry.oid)
    assert stored_log_entry == existing_log_entry


def test_add_log_entry_allows_none_app_user_oid(db, existing_log_entry):
    no_user_log_entry = copy.copy(existing_log_entry)
    no_user_log_entry.oid = existing_log_entry.oid + 1
    no_user_log_entry.app_user_oid = None
    no_user_log_entry.app_user_name = None
    db.add_log_entry(no_user_log_entry)
    stored_log_entry = db.get_log_entry_by_oid(no_user_log_entry.oid)
    assert stored_log_entry == no_user_log_entry


def test_get_last_log_entry_gets_last_one(db, existing_log_entry):
    new_log_entry = copy.copy(existing_log_entry)
    new_log_entry.oid = db.add_log_entry(new_log_entry)
    assert db.get_last_log_entry() == new_log_entry


def test_get_last_log_entry_when_none_raises(db):
    regex = "there are no log entry records"
    with pytest.raises(DatastoreKeyError, match=regex):
        db.get_last_log_entry()
