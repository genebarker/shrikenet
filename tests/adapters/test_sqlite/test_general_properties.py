from datetime import datetime

import pytest

from shrikenet.adapters.sqlite import SQLite
from shrikenet.entities.exceptions import (
    DatastoreAlreadyOpen,
    DatastoreError,
)
from shrikenet.entities.storage_provider import StorageProvider

DATABASE = "test.db"


@pytest.fixture
def db():
    database = SQLite(DATABASE)
    database.open()
    yield database
    database.close()


@pytest.fixture
def unopened_db():
    return SQLite(DATABASE)


def test_is_a_storage_provider(db):
    assert isinstance(db, StorageProvider)


def test_get_version_returns_provider_info(db):
    assert db.get_version().startswith("SQLite version 3.")


def test_raises_when_not_opened_first(unopened_db):
    with pytest.raises(DatastoreError) as excinfo:
        unopened_db.get_version()
    assert str(excinfo.value).startswith("can not get version information")


def test_raises_on_open_when_already_opened(db):
    with pytest.raises(DatastoreAlreadyOpen) as excinfo:
        db.open()
    assert str(excinfo.value) == "connection already open"


def test_raises_on_access_after_closed(unopened_db):
    db = unopened_db
    db.open()
    db.close()
    with pytest.raises(DatastoreError) as excinfo:
        db.get_version()
    assert "closed database" in str(excinfo.value)


def test_datetime_to_sql_converts_to_expected_string(db):
    nye_2024 = datetime(
        year=2024,
        month=1,
        day=1,
        hour=0,
        minute=2,
        second=3,
        microsecond=123456,
    )
    sql_nye = db.datetime_to_sql(nye_2024)
    assert sql_nye == "2024-01-01T00:02:03.123456"


def test_sql_to_datetime_converts_to_expected_time(db):
    boxing_2023 = datetime(
        year=2023,
        month=12,
        day=26,
        hour=14,
        minute=1,
        second=2,
        microsecond=334455,
    )
    sql_boxing = "2023-12-26T14:01:02.334455"
    assert db.sql_to_datetime(sql_boxing) == boxing_2023
