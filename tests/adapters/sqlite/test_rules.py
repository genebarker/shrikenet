import pytest

from shrikenet.adapters.sqlite import SQLiteAdapter
from shrikenet.entities.rules import Rules

DATABASE = "test.db"


@pytest.fixture
def db():
    database = SQLiteAdapter(DATABASE)
    database.open()
    database.build_database_schema()
    yield database
    database.close()


def test_get_rules_returns_rules_object(db):
    rules = db.get_rules()
    assert isinstance(rules, Rules)


def test_initial_rules_are_set_to_defaults(db):
    rules = db.get_rules()
    default_rules = Rules()
    assert rules == default_rules


def test_save_rules_saves_them(db):
    rules_a = create_and_store_sample_rules(db)
    rules_b = db.get_rules()
    assert rules_a == rules_b


def create_and_store_sample_rules(db):
    rules = create_sample_rules()
    db.save_rules(rules)
    return rules


def create_sample_rules():
    rules = Rules()
    rules.login_fail_threshold_count = 42
    return rules


def test_rules_exist_after_commit(db):
    rules = create_and_store_sample_rules(db)
    db.commit()
    assert rules == db.get_rules()


def test_rules_gone_after_rollback(db):
    rules = create_and_store_sample_rules(db)
    db.commit()
    rules.login_fail_threshold_count = 99
    db.save_rules(rules)
    db.rollback()
    assert create_sample_rules() == db.get_rules()
