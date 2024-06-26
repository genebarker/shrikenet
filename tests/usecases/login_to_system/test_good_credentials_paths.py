from datetime import datetime, timedelta

from shrikenet.entities.log_entry_tag import LogEntryTag
from shrikenet.usecases.login_to_system import LoginToSystem
from tests.usecases.login_to_system.setup_class import (
    SetupClass,
    GOOD_USER_USERNAME,
    GOOD_USER_PASSWORD,
    GOOD_IP_ADDRESS,
)


class TestGoodCredentialPaths(SetupClass):

    def test_login_succeeds_for_good_credentials(self):
        good_user = self.create_good_user()
        login_to_system = LoginToSystem(self.services)
        result = login_to_system.run(
            GOOD_USER_USERNAME, GOOD_USER_PASSWORD, GOOD_IP_ADDRESS
        )
        self.validate_successful_result(
            good_user, result, "Login successful."
        )

    def test_successful_login_logs(self, caplog):
        self.create_and_store_user("joe", "some_password")
        login_to_system = LoginToSystem(self.services)
        login_to_system.run("joe", "some_password", "4.3.2.1")
        self.validate_log_entry(
            caplog,
            "App user (username=joe) from 4.3.2.1 successfully logged in.",
        )

    def test_successful_login_recorded(self):
        user = self.create_and_store_user("max", "some_password")
        time_before = datetime.now() - timedelta(seconds=1)
        login_to_system = LoginToSystem(self.services)
        login_to_system.run("max", "some_password", "1.2.3.4")
        expected_text = (
            "App user (username=max) from 1.2.3.4 "
            "successfully logged in."
        )
        self.validate_log_entry_recorded(
            time_before=time_before,
            app_user_oid=user.oid,
            tag=LogEntryTag.user_login,
            text=expected_text,
            usecase_tag="login_to_system",
        )

    def test_password_fail_count_reset_on_successful_login(self):
        self.perform_login_to_reset_password_fail_count()
        user = self.db.get_app_user_by_username(GOOD_USER_USERNAME)
        assert user.ongoing_password_failure_count == 0

    def perform_login_to_reset_password_fail_count(self):
        user = self.create_good_user()
        user.ongoing_password_failure_count = 2
        self.db.update_app_user(user)
        login_to_system = LoginToSystem(self.services)
        login_to_system.run(
            GOOD_USER_USERNAME, GOOD_USER_PASSWORD, GOOD_IP_ADDRESS
        )

    def test_user_record_change_is_committed(self):
        self.perform_login_to_reset_password_fail_count()
        self.db.rollback()
        user = self.db.get_app_user_by_username(GOOD_USER_USERNAME)
        assert user.ongoing_password_failure_count == 0
