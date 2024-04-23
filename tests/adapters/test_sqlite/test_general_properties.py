import pytest

from shrikenet.adapters.sqlite import SQLite
from shrikenet.entities.exceptions import (
    DatastoreAlreadyOpen,
    DatastoreClosed,
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
