import pytest

from shrikenet.entities.exceptions import (
    DatastoreClosed,
    DatastoreAlreadyOpen,
)
from shrikenet.entities.storage_provider import StorageProvider


def test_is_a_storage_provider(db):
    assert isinstance(db, StorageProvider)


def test_get_version_returns_provider_info(db):
    assert db.get_version().startswith(db.VERSION_PREFIX)


def test_raises_when_not_opened_first(unopened_db):
    with pytest.raises(DatastoreClosed) as excinfo:
        unopened_db.get_version()
    assert str(excinfo.value) == (
        "get_version is not available since the connection is closed"
    )


def test_raises_when_already_opened(db):
    with pytest.raises(DatastoreAlreadyOpen) as excinfo:
        db.open()
    assert str(excinfo.value) == "connection already open"


def test_raises_when_already_closed(unopened_db):
    db = unopened_db
    db.open()
    db.close()
    with pytest.raises(DatastoreClosed):
        db.get_version()
