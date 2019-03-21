import pytest
from shrike.entities.app_user import AppUser

GOOD_ID = 100
GOOD_USERNAME = 'fmulder'
GOOD_NAME = 'Fox Mulder'
GOOD_PASSWORD_HASH = 'xxxYYY'

class TestGeneralProperties:

    def test_minimal_init(self):
        user = AppUser(GOOD_USERNAME, GOOD_NAME, GOOD_PASSWORD_HASH)
        assert user.id is None
        assert user.username == GOOD_USERNAME
        assert user.name == GOOD_NAME
        assert user.password_hash == GOOD_PASSWORD_HASH


class TestEquals:

    def test_equals(self):
        user_one = AppUser(GOOD_USERNAME, GOOD_NAME, GOOD_PASSWORD_HASH)
        user_two = AppUser(GOOD_USERNAME, GOOD_NAME, GOOD_PASSWORD_HASH)
        assert user_one == user_two

    def test_unequal_when_class_different(self):
        class FakeUser:
            def __init__(self, username, name, password_hash):
                self.username = username
                self.name = name
                self.password_hash = password_hash
        
        user_one = AppUser(GOOD_USERNAME, GOOD_NAME, GOOD_PASSWORD_HASH)
        user_two = FakeUser(GOOD_USERNAME, GOOD_NAME, GOOD_PASSWORD_HASH)
        assert user_one != user_two

    @pytest.mark.parametrize(('id', 'username', 'name', 'password_hash'), (
        (999, GOOD_USERNAME, GOOD_NAME, GOOD_PASSWORD_HASH),
        (GOOD_ID, 'otherusername', GOOD_NAME, GOOD_PASSWORD_HASH),
        (GOOD_ID, GOOD_USERNAME, 'Other Name', GOOD_PASSWORD_HASH),
        (GOOD_ID, GOOD_USERNAME, GOOD_NAME, 'otherHASH'),
    ))
    def test_unequal_when_attribute_different(self, id, username, name, password_hash):
        user_one = AppUser(GOOD_USERNAME, GOOD_NAME, GOOD_PASSWORD_HASH)
        user_one.id = GOOD_ID
        user_two = AppUser(username, name, password_hash)
        user_two.id = id
        assert user_one != user_two
