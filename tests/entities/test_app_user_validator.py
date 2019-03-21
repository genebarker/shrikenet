import pytest
from shrike.entities.app_user import AppUser
from shrike.entities.app_user_validator import AppUserValidator


GOOD_USERNAME = 'fmulder'
GOOD_NAME = 'Fox Mulder'
GOOD_PASSWORD_HASH = 'xxxYYY'

class TestFieldValidation:

    def test_username_required(self):
        app_user = AppUser(None, GOOD_NAME, GOOD_PASSWORD_HASH)
        self.verify_validation_raises(app_user)

    @staticmethod
    def verify_validation_raises(app_user):
        with pytest.raises(ValueError):
            AppUserValidator.validate_fields(app_user)

    def test_username_validated(self):
        app_user = AppUser('bad username', GOOD_NAME, GOOD_PASSWORD_HASH)
        self.verify_validation_raises(app_user)

    def test_name_required(self):
        app_user = AppUser(GOOD_USERNAME, None, GOOD_PASSWORD_HASH)
        self.verify_validation_raises(app_user)

    def test_name_validated(self):
        app_user = AppUser(GOOD_USERNAME, 'A *bad* Name', GOOD_PASSWORD_HASH)
        self.verify_validation_raises(app_user)
