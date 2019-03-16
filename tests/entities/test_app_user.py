import pytest
from shrike.entities.app_user import AppUser

GOOD_USERNAME = 'mrgood'
GOOD_NAME = 'Mr. Good'
GOOD_PASSWORD_HASH = 'xxxYYY'

class TestGeneralProperties:

    def test_minimal_init(self):
        user = AppUser(GOOD_USERNAME, GOOD_NAME, GOOD_PASSWORD_HASH)
        assert user.username == GOOD_USERNAME
        assert user.name == GOOD_NAME
        assert user.password_hash == GOOD_PASSWORD_HASH

    def test_field_validation_performed_on_init(self):
        with pytest.raises(ValueError):
            AppUser(None, None, None)

class TestFieldValidation:

    def test_username_required(self):
        with pytest.raises(ValueError):
            AppUser(None, GOOD_NAME, GOOD_PASSWORD_HASH)

    def test_username_validated(self):
        with pytest.raises(ValueError):
            AppUser('bad username', GOOD_NAME, GOOD_PASSWORD_HASH)

    def test_name_required(self):
        with pytest.raises(ValueError):
            AppUser(GOOD_USERNAME, None, GOOD_PASSWORD_HASH)

    def test_name_validated(self):
        with pytest.raises(ValueError):
            AppUser(GOOD_USERNAME, 'A *bad* Name', GOOD_PASSWORD_HASH)

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

    @pytest.mark.parametrize(('username', 'name', 'password_hash'), (
        ('otherusername', GOOD_NAME, GOOD_PASSWORD_HASH),
        (GOOD_USERNAME, 'Other Name', GOOD_PASSWORD_HASH),
        (GOOD_USERNAME, GOOD_NAME, 'otherHASH'),
    ))
    def test_unequal_when_attribute_different(self, username, name, password_hash):
        user_one = AppUser(GOOD_USERNAME, GOOD_NAME, GOOD_PASSWORD_HASH)
        user_two = AppUser(username, name, password_hash)
        assert user_one != user_two
