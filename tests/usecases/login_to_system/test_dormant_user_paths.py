import pytest

from tests.usecases.login_to_system.setup_class import (
    SetupClass,
    GOOD_USER_USERNAME,
    GOOD_USER_PASSWORD,
)


class TestDormantUserPaths(SetupClass):

    def test_login_fails_when_user_dormant(self):
        self.create_dormant_user()
        self.validate_login_fails(
            GOOD_USER_USERNAME, GOOD_USER_PASSWORD,
            message='Login attempt failed. Your credentials are invalid.'
        )

    def create_dormant_user(self):
        user = self.create_user(GOOD_USER_USERNAME, GOOD_USER_PASSWORD)
        user.is_dormant = True
        self.db.add_app_user(user)
        return user

    def test_dormant_checked_before_password(self):
        self.create_dormant_user()
        self.validate_login_fails(
            GOOD_USER_USERNAME, 'wrong_password',
            message='Login attempt failed. Your credentials are invalid.'
        )
