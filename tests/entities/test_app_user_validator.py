import pytest

from shrikenet.entities.app_user import AppUser
from shrikenet.entities.app_user_validator import AppUserValidator
from shrikenet.entities.record_validator import RecordValidator

from tests.entities.test_app_user import create_good_app_user


class TestGeneralProperties:

    def test_is_a_record_validator(self):
        assert issubclass(AppUserValidator, RecordValidator)


class TestFieldValidation:

    def test_successful_validation_returns_none(self):
        app_user = create_good_app_user()
        assert AppUserValidator.validate_fields(app_user) is None

    def test_oid_required(self):
        app_user = create_good_app_user()
        app_user.oid = None
        self.verify_validation_raises(app_user)

    @staticmethod
    def verify_validation_raises(app_user):
        with pytest.raises(ValueError):
            AppUserValidator.validate_fields(app_user)

    def test_oid_validated(self):
        app_user = create_good_app_user()
        app_user.oid = "bad oid"
        self.verify_validation_raises(app_user)

    def test_username_required(self):
        app_user = create_good_app_user()
        app_user.username = None
        self.verify_validation_raises(app_user)

    def test_username_validated(self):
        app_user = create_good_app_user()
        app_user.username = "bad username"
        self.verify_validation_raises(app_user)

    def test_name_required(self):
        app_user = create_good_app_user()
        app_user.name = None
        self.verify_validation_raises(app_user)

    def test_name_validated(self):
        app_user = create_good_app_user()
        app_user.name = "A *bad* Name"
        self.verify_validation_raises(app_user)


class TestReferenceValidation:

    def test_successful_validation_returns_none(self):
        app_user = create_good_app_user()
        assert AppUserValidator.validate_references(app_user, None) is None
