import copy
from datetime import datetime, timezone

import pytest

from shrikenet.entities.app_user import AppUser


GOOD_OID = 100
GOOD_USERNAME = 'fmulder'
GOOD_NAME = 'Fox Mulder'
GOOD_PASSWORD_HASH = 'xxxYYY'
DEFAULT_NEEDS_PASSWORD_CHANGE = False
DEFAULT_IS_LOCKED = False
DEFAULT_IS_DORMANT = False
DEFAULT_FAILURE_COUNT = 0
DEFAULT_FAILURE_TIME = None


def create_good_app_user():
    return AppUser(
        oid=GOOD_OID,
        username=GOOD_USERNAME,
        name=GOOD_NAME,
        password_hash=GOOD_PASSWORD_HASH,
        )


def test_minimal_init():
    user = create_good_app_user()
    assert user.oid == GOOD_OID
    assert user.username == GOOD_USERNAME
    assert user.name == GOOD_NAME
    assert user.password_hash == GOOD_PASSWORD_HASH
    assert user.needs_password_change is DEFAULT_NEEDS_PASSWORD_CHANGE
    assert user.is_locked is DEFAULT_IS_LOCKED
    assert user.is_dormant is DEFAULT_IS_DORMANT
    assert user.ongoing_password_failure_count == DEFAULT_FAILURE_COUNT
    assert user.last_password_failure_time == DEFAULT_FAILURE_TIME
