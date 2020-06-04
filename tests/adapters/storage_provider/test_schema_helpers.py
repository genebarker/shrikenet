import pytest


def test_schema_exists_after_build(db):
    db.build_database_schema()
    assert_database_in_initial_state(db)


def assert_database_in_initial_state(db):
    assert db.get_app_user_count() == 0
    assert db.get_post_count() == 0
    assert db.get_next_app_user_oid() == 1
    assert db.get_next_post_oid() == 1


def test_database_objects_reset_to_initial_state(db):
    db.reset_database_objects()
    assert_database_in_initial_state(db)
