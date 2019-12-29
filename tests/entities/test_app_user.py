import pytest

from shrike.entities.app_user import AppUser


GOOD_OID = 100
GOOD_USERNAME = 'fmulder'
GOOD_NAME = 'Fox Mulder'
GOOD_PASSWORD_HASH = 'xxxYYY'
DEFAULT_NEEDS_PASSWORD_CHANGE = False
DEFAULT_IS_LOCKED = False


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


class TestEquals:

    def test_equals(self):
        user_one = create_good_app_user()
        user_two = create_good_app_user()
        assert user_one == user_two

    def test_unequal_when_class_different(self):
        class FakeUser:
            def __init__(self, oid, username, name, password_hash,
                         needs_password_change, is_locked):
                self.oid = oid
                self.username = username
                self.name = name
                self.password_hash = password_hash
                self.needs_password_change = needs_password_change
                self.is_locked = is_locked

        user_one = AppUser(GOOD_OID, GOOD_USERNAME, GOOD_NAME,
                           GOOD_PASSWORD_HASH,
                           DEFAULT_NEEDS_PASSWORD_CHANGE,
                           DEFAULT_IS_LOCKED)
        user_two = FakeUser(GOOD_OID, GOOD_USERNAME, GOOD_NAME,
                            GOOD_PASSWORD_HASH,
                            DEFAULT_NEEDS_PASSWORD_CHANGE,
                            DEFAULT_IS_LOCKED)
        assert user_one != user_two

    @pytest.mark.parametrize(
        ('oid', 'username', 'name', 'password_hash',
         'needs_password_change', 'is_locked'),
        (
            (999, GOOD_USERNAME, GOOD_NAME, GOOD_PASSWORD_HASH,
             DEFAULT_NEEDS_PASSWORD_CHANGE, DEFAULT_IS_LOCKED),
            (GOOD_OID, 'otherusername', GOOD_NAME, GOOD_PASSWORD_HASH,
             DEFAULT_NEEDS_PASSWORD_CHANGE, DEFAULT_IS_LOCKED),
            (GOOD_OID, GOOD_USERNAME, 'Other Name', GOOD_PASSWORD_HASH,
             DEFAULT_NEEDS_PASSWORD_CHANGE, DEFAULT_IS_LOCKED),
            (GOOD_OID, GOOD_USERNAME, GOOD_NAME, 'otherHASH',
             DEFAULT_NEEDS_PASSWORD_CHANGE, DEFAULT_IS_LOCKED),
            (GOOD_OID, GOOD_USERNAME, GOOD_NAME, GOOD_PASSWORD_HASH,
             not DEFAULT_NEEDS_PASSWORD_CHANGE, DEFAULT_IS_LOCKED),
            (GOOD_OID, GOOD_USERNAME, GOOD_NAME, GOOD_PASSWORD_HASH,
             DEFAULT_NEEDS_PASSWORD_CHANGE, not DEFAULT_IS_LOCKED),
        )
    )
    def test_unequal_when_attribute_different(
            self, oid, username, name, password_hash,
            needs_password_change, is_locked):
        user_one = AppUser(GOOD_OID, GOOD_USERNAME, GOOD_NAME,
                           GOOD_PASSWORD_HASH,
                           DEFAULT_NEEDS_PASSWORD_CHANGE,
                           DEFAULT_IS_LOCKED)
        user_two = AppUser(oid, username, name, password_hash,
                           needs_password_change, is_locked)
        assert user_one != user_two
