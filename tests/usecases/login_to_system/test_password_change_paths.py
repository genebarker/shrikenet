from datetime import datetime, timedelta

from shrikenet.entities.log_entry_tag import LogEntryTag
from shrikenet.usecases.login_to_system import LoginToSystem
from tests.usecases.login_to_system.setup_class import (
    SetupClass,
    GOOD_USER_USERNAME,
    GOOD_USER_PASSWORD,
    GOOD_IP_ADDRESS,
)


class TestPasswordChangePaths(SetupClass):

    def test_login_fails_when_password_marked_for_reset(self):
        self.create_needs_password_change_user()
        login_to_system = LoginToSystem(self.services)
        result = login_to_system.run(
            GOOD_USER_USERNAME, GOOD_USER_PASSWORD, GOOD_IP_ADDRESS
        )
        assert result.has_failed
        assert result.must_change_password
        assert result.message == (
            "Password marked for reset. Must supply a new password."
        )

    def create_needs_password_change_user(
        self, username=GOOD_USER_USERNAME, password=GOOD_USER_PASSWORD
    ):
        user = self.create_and_store_user(username, password)
        user.needs_password_change = True
        self.db.update_app_user(user)
        return user

    def test_password_marked_for_reset_failure_logs(self, caplog):
        self.create_needs_password_change_user("jack", GOOD_USER_PASSWORD)
        login_to_system = LoginToSystem(self.services)
        login_to_system.run("jack", GOOD_USER_PASSWORD, "4.3.2.1")
        self.validate_log_entry(
            caplog,
            "App user (username=jack) with password marked for reset from "
            "4.3.2.1 attempted to login without providing a new password.",
        )

    def test_password_marked_for_reset_failure_recorded(self):
        user = self.create_needs_password_change_user(
            username="jill", password="some_password"
        )
        time_before = datetime.now() - timedelta(seconds=1)
        login_to_system = LoginToSystem(self.services)
        login_to_system.run("jill", "some_password", "4.5.6.7")
        expected_text = (
            "App user (username=jill) with password marked "
            "for reset from 4.5.6.7 attempted to login "
            "without providing a new password."
        )
        self.validate_log_entry_recorded(
            time_before=time_before,
            app_user_oid=user.oid,
            tag=LogEntryTag.must_change_password,
            text=expected_text,
            usecase_tag=LoginToSystem.USECASE_TAG,
        )

    def test_password_marked_for_reset_succeeds_when_new_provided(self):
        user = self.create_needs_password_change_user()
        result = self.perform_good_password_change_login(
            user, GOOD_USER_PASSWORD
        )
        self.validate_successful_password_change_result(user, result)

    def perform_good_password_change_login(
        self, user, current_password, ip_address=GOOD_IP_ADDRESS
    ):
        login_to_system = LoginToSystem(self.services)
        new_password = self.reverse_string(current_password)
        return login_to_system.run(
            user.username, current_password, ip_address, new_password
        )

    def reverse_string(self, string):
        return string[::-1]

    def validate_successful_password_change_result(self, user, result):
        self.validate_successful_result(
            user, result, "Login successful. Password successfully changed."
        )

    def test_password_change_logged(self, caplog):
        user = self.create_needs_password_change_user(
            "jane", GOOD_USER_PASSWORD
        )
        self.perform_good_password_change_login(
            user, GOOD_USER_PASSWORD, "2.1.1.2"
        )
        self.validate_log_entry(
            caplog,
            "App user (username=jane) from 2.1.1.2 successfully "
            "logged in. Password successfully changed.",
        )

    def test_password_change_recorded(self, caplog):
        user = self.create_needs_password_change_user(
            "clark", GOOD_USER_PASSWORD
        )
        time_before = datetime.now() - timedelta(seconds=1)

        self.perform_good_password_change_login(
            user, GOOD_USER_PASSWORD, "9.8.7.6"
        )

        expected_text = (
            "App user (username=clark) from 9.8.7.6 successfully "
            "logged in. Password successfully changed."
        )
        self.validate_log_entry_recorded(
            time_before=time_before,
            app_user_oid=user.oid,
            tag=LogEntryTag.user_login,
            text=expected_text,
            usecase_tag=LoginToSystem.USECASE_TAG,
        )

    def test_password_marked_for_reset_clears_after_new_provided(self):
        user = self.create_needs_password_change_user()
        self.perform_good_password_change_login(user, GOOD_USER_PASSWORD)
        user = self.db.get_app_user_by_oid(user.oid)
        assert not user.needs_password_change

    def test_credentials_checked_before_password_reset(self):
        self.create_needs_password_change_user()
        self.validate_login_fails(GOOD_USER_USERNAME, "wrong_pwd")

    def test_password_change_returns_successful_result(self):
        good_user = self.create_good_user()
        result = self.perform_good_password_change_login(
            good_user, GOOD_USER_PASSWORD
        )
        self.validate_successful_password_change_result(good_user, result)

    def test_password_change_is_committed(self):
        good_user = self.create_good_user()
        login_to_system = LoginToSystem(self.services)
        new_password = self.reverse_string(GOOD_USER_PASSWORD)
        login_to_system.run(
            GOOD_USER_USERNAME,
            GOOD_USER_PASSWORD,
            GOOD_IP_ADDRESS,
            new_password,
        )
        self.db.rollback()
        user = self.db.get_app_user_by_oid(good_user.oid)
        assert self.crypto.hash_matches_string(
            user.password_hash, new_password
        )

    def test_fails_when_new_password_is_the_same(self):
        user = self.create_good_user()
        login_to_system = LoginToSystem(self.services)
        result = login_to_system.run(
            user.username,
            GOOD_USER_PASSWORD,
            GOOD_IP_ADDRESS,
            GOOD_USER_PASSWORD,
        )
        assert result.has_failed
        assert result.message == (
            "Password change failed. New password can not be the same as "
            "the current one."
        )

    def test_fails_when_new_password_is_too_weak(self):
        user = self.create_good_user()
        weak_password = "password"
        login_to_system = LoginToSystem(self.services)
        result = login_to_system.run(
            user.username,
            GOOD_USER_PASSWORD,
            GOOD_IP_ADDRESS,
            weak_password,
        )
        assert result.has_failed
        assert result.message.startswith(
            "Password change failed. New password is too weak. "
            "Suggestions: "
        )
