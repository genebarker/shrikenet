import pytest
from shrike.entities.app_user import AppUser
from shrike.entities.app_user_validator import AppUserValidator
from .test_app_user import create_good_app_user


class TestFieldValidation:

    def test_id_required(self):
        app_user = create_good_app_user()
        app_user.id = None
        self.verify_validation_raises(app_user)

    @staticmethod
    def verify_validation_raises(app_user):
        with pytest.raises(ValueError):
            AppUserValidator.validate_fields(app_user)

    def test_username_required(self):
        app_user = create_good_app_user()
        app_user.username = None
        self.verify_validation_raises(app_user)

    def test_username_validated(self):
        app_user = create_good_app_user()
        app_user.username = 'bad username'
        self.verify_validation_raises(app_user)

    def test_name_required(self):
        app_user = create_good_app_user()
        app_user.name = None
        self.verify_validation_raises(app_user)

    def test_name_validated(self):
        app_user = create_good_app_user()
        app_user.name = 'A *bad* Name'
        self.verify_validation_raises(app_user)
