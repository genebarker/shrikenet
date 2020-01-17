import pytest

from shrike.usecases.login_to_system import LoginToSystem
from tests.usecases.login_to_system.setup_class import (
    SetupClass,
    GOOD_USER_USERNAME,
    GOOD_USER_PASSWORD,
    GOOD_IP_ADDRESS,
)


class TestNeedsPasswordChangePaths(SetupClass):

    def test_login_fails_when_password_marked_for_reset(self):
        self.create_needs_password_change_user()
        login_to_system = LoginToSystem(self.services)
        result = login_to_system.run(GOOD_USER_USERNAME, GOOD_USER_PASSWORD,
                                     GOOD_IP_ADDRESS)
        assert result.has_failed
        assert result.must_change_password
        assert result.message == ('Password marked for reset. Must supply '
                                  'a new password.')

    def create_needs_password_change_user(self):
        user = self.create_good_user()
        user.needs_password_change = True
        self.db.update_app_user(user)
        return user

    def test_login_succeeds_when_new_provided(self):
        user = self.create_needs_password_change_user()
        login_to_system = LoginToSystem(self.services)
        new_password = self.reverse_string(GOOD_USER_PASSWORD)
        result = login_to_system.run(GOOD_USER_USERNAME, GOOD_USER_PASSWORD,
                                     GOOD_IP_ADDRESS, new_password)
        self.validate_successful_password_change_result(user, result)

    def reverse_string(self, string):
        return string[::-1]

    def validate_successful_password_change_result(self, user, result):
        self.validate_successful_result(
            user, result, 'Login successful. Password successfully changed.'
        )

    def test_credentials_checked_before_password_reset(self):
        self.create_needs_password_change_user()
        self.validate_login_fails(GOOD_USER_USERNAME, 'wrong_pwd')

    def test_password_change_returns_successful_result(self):
        good_user = self.create_good_user()
        login_to_system = LoginToSystem(self.services)
        new_password = self.reverse_string(GOOD_USER_PASSWORD)
        result = login_to_system.run(GOOD_USER_USERNAME, GOOD_USER_PASSWORD,
                                     GOOD_IP_ADDRESS, new_password)
        self.validate_successful_password_change_result(good_user, result)

    def test_password_change_is_committed(self):
        good_user = self.create_good_user()
        login_to_system = LoginToSystem(self.services)
        new_password = self.reverse_string(GOOD_USER_PASSWORD)
        login_to_system.run(GOOD_USER_USERNAME, GOOD_USER_PASSWORD,
                            GOOD_IP_ADDRESS, new_password)
        self.db.rollback()
        user = self.db.get_app_user_by_oid(good_user.oid)
        assert self.crypto.hash_matches_string(user.password_hash,
                                               new_password)
