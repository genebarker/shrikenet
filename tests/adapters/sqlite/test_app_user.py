import copy
from datetime import datetime, timedelta

import pytest

from shrikenet.entities.app_user import AppUser
from shrikenet.entities.exceptions import (
    DatastoreError,
    DatastoreKeyError,
)


def create_and_add_user(db):
    app_user = create_user()
    app_user.oid = db.add_app_user(app_user)
    return app_user


def create_user():
    oid = -1
    username = "mawesome"
    name = "Mr. Awesome"
    password_hash = "xxYYYzzzz"
    time_now = datetime.now()
    app_user = AppUser(
        oid,
        username,
        name,
        password_hash,
        needs_password_change=True,
        is_locked=True,
        is_dormant=True,
        ongoing_password_failure_count=2,
        last_password_failure_time=time_now,
    )
    return app_user


def test_add_user_returns_oid(db):
    app_user = create_user()
    app_user.oid = db.add_app_user(app_user)
    assert app_user.oid > 0


def test_get_app_user_by_username_unknown_raises(db):
    regex = "can not get app_user .username=xyz., reason: "
    with pytest.raises(DatastoreKeyError, match=regex):
        db.get_app_user_by_username("xyz")


def test_get_app_user_by_username_gets_record(db):
    original_user = create_and_add_user(db)
    stored_user = db.get_app_user_by_username(original_user.username)
    assert stored_user == original_user


def test_get_app_user_by_oid_unknown_raises(db):
    regex = "can not get app_user .oid=12345., reason: "
    with pytest.raises(DatastoreKeyError, match=regex):
        db.get_app_user_by_oid("12345")


def test_add_app_user_adds_record(db):
    app_user = create_and_add_user(db)
    stored_user = db.get_app_user_by_oid(app_user.oid)
    assert stored_user == app_user


def test_add_app_user_with_duplicate_username_raises(db):
    app_user = create_and_add_user(db)
    new_user = copy.copy(app_user)
    regex = "can not add app_user .username=mawesome., reason: "
    with pytest.raises(DatastoreError, match=regex):
        db.add_app_user(new_user)


def test_update_app_user_updates_record(db):
    app_user = create_and_add_user(db)
    app_user.name = "Different"
    db.update_app_user(app_user)
    stored_user = db.get_app_user_by_oid(app_user.oid)
    assert stored_user == app_user


def test_update_app_user_updates_every_field(db):
    app_user = create_and_add_user(db)
    app_user.username += "a"
    app_user.name += "b"
    app_user.password_hash += "c"
    app_user.needs_password_change = not app_user.needs_password_change
    app_user.is_locked = not app_user.is_locked
    app_user.is_dormant = not app_user.is_dormant
    app_user.ongoing_password_failure_count += 1
    app_user.last_password_failure_time = (
        app_user.last_password_failure_time - timedelta(hours=1)
    )
    db.update_app_user(app_user)
    stored_user = db.get_app_user_by_oid(app_user.oid)
    assert stored_user == app_user


def test_update_app_user_raises_on_unknown_oid(db):
    user = AppUser(12345, "mrunknown", "Mr Unkonwn", "fakeHASH")
    regex = "can not update app_user .oid=12345., reason: "
    with pytest.raises(DatastoreKeyError, match=regex):
        db.update_app_user(user)


def test_get_app_user_count_zero_when_empty(db):
    assert db.get_app_user_count() == 0


def test_get_app_user_count_matches_that_stored(db):
    create_and_add_user(db)
    assert db.get_app_user_count() == 1


def test_exists_app_user_true_for_known(db):
    app_user = create_and_add_user(db)
    assert db.exists_app_username(app_user.username)


def test_exists_app_user_false_for_unknown(db):
    assert db.exists_app_username("UNKNOWN") is False


def test_add_app_user_record_exists_after_commit(db):
    app_user = create_and_add_user(db)
    db.commit()
    assert db.exists_app_username(app_user.username)


def test_add_app_user_record_gone_after_rollback(db):
    app_user = create_and_add_user(db)
    db.rollback()
    assert not db.exists_app_username(app_user.username)
