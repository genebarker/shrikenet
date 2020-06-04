import pytest


def test_commit_can_be_called_after_no_action(db):
    db.commit()
    db.commit()


def test_rollback_can_be_called_after_no_action(db):
    db.rollback()
    db.rollback()
