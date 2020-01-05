import copy
from datetime import datetime, timezone

import pytest

from shrike.entities.app_user import AppUser


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


class TestGeneralProperties:

    def test_minimal_init(self):
        user = create_good_app_user()
        assert user.oid == GOOD_OID
        assert user.username == GOOD_USERNAME
        assert user.name == GOOD_NAME
        assert user.password_hash == GOOD_PASSWORD_HASH
        assert user.needs_password_change is DEFAULT_NEEDS_PASSWORD_CHANGE
        assert user.is_locked is DEFAULT_IS_LOCKED
        assert user.is_dormant is DEFAULT_IS_DORMANT
        assert user.ongoing_login_failure_count == DEFAULT_FAILURE_COUNT
        assert user.last_login_failure_time == DEFAULT_FAILURE_TIME


class TestEquals:

    def test_equals(self):
        user_one = create_good_app_user()
        user_two = create_good_app_user()
        assert user_one == user_two

    def test_unequal_when_class_different(self):
        class FakeUser:
            def __init__(self, oid, username, name, password_hash,
                         needs_password_change, is_locked, is_dormant,
                         ongoing_login_failure_count,
                         last_login_failure_time):
                self.oid = oid
                self.username = username
                self.name = name
                self.password_hash = password_hash
                self.needs_password_change = needs_password_change
                self.is_locked = is_locked
                self.is_dormant = is_dormant
                self.ongoing_login_failure_count = ongoing_login_failure_count
                self.last_login_failure_time = last_login_failure_time

        user_one = AppUser(GOOD_OID, GOOD_USERNAME, GOOD_NAME,
                           GOOD_PASSWORD_HASH,
                           DEFAULT_NEEDS_PASSWORD_CHANGE,
                           DEFAULT_IS_LOCKED, DEFAULT_IS_DORMANT,
                           DEFAULT_FAILURE_COUNT, DEFAULT_FAILURE_TIME)
        user_two = FakeUser(GOOD_OID, GOOD_USERNAME, GOOD_NAME,
                            GOOD_PASSWORD_HASH,
                            DEFAULT_NEEDS_PASSWORD_CHANGE,
                            DEFAULT_IS_LOCKED, DEFAULT_IS_DORMANT,
                            DEFAULT_FAILURE_COUNT, DEFAULT_FAILURE_TIME)
        assert user_one != user_two

    @pytest.mark.parametrize(
        ('attribute_name', 'attribute_value'),
        (
            ('oid', 999),
            ('username', 'otherusername'),
            ('name', 'Other Name'),
            ('password_hash', 'otherHASH'),
            ('needs_password_change', not DEFAULT_NEEDS_PASSWORD_CHANGE),
            ('is_locked', not DEFAULT_IS_LOCKED),
            ('is_dormant', not DEFAULT_IS_DORMANT),
            ('ongoing_login_failure_count', 999),
            ('last_login_failure_time', datetime.now(timezone.utc)),
        )
    )
    def test_unequal_when_attribute_different(self, attribute_name,
                                              attribute_value):
        user_one = AppUser(GOOD_OID, GOOD_USERNAME, GOOD_NAME,
                           GOOD_PASSWORD_HASH,
                           DEFAULT_NEEDS_PASSWORD_CHANGE,
                           DEFAULT_IS_LOCKED,
                           DEFAULT_IS_DORMANT,
                           DEFAULT_FAILURE_COUNT,
                           DEFAULT_FAILURE_TIME)
        user_two = copy.deepcopy(user_one)
        setattr(user_two, attribute_name, attribute_value)
        assert user_one != user_two
