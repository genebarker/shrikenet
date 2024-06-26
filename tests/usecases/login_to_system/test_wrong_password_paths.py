from datetime import datetime, timedelta

from shrikenet.entities.log_entry_tag import LogEntryTag
from shrikenet.usecases.login_to_system import LoginToSystem
from tests.usecases.login_to_system.setup_class import (
    SetupClass,
    GOOD_USER_USERNAME,
    GOOD_USER_PASSWORD,
    GOOD_IP_ADDRESS,
)


class TestWrongPasswordPaths(SetupClass):

    def test_login_fails_on_wrong_password(self):
        self.create_good_user()
        self.validate_login_fails(GOOD_USER_USERNAME, "wrong_password")

    def test_wrong_password_occurrence_logs(self, caplog):
        self.create_and_store_user("mrunhappy", GOOD_USER_PASSWORD)
        login_to_system = LoginToSystem(self.services)
        login_to_system.run("mrunhappy", "wrong_password", "1.2.3.4")
        self.validate_log_entry(
            caplog,
            "App user (username=mrunhappy) from 1.2.3.4 attempted "
            "to login with the wrong password "
            "(ongoing_password_failure_count=1).",
        )

    def test_wrong_password_occurrence_recorded(self):
        user = self.create_and_store_user("mrforgetful", GOOD_USER_PASSWORD)
        time_before = datetime.now() - timedelta(seconds=1)
        login_to_system = LoginToSystem(self.services)
        login_to_system.run("mrforgetful", "wrong_password", "1.2.3.4")
        expected_text = (
            "App user (username=mrforgetful) from 1.2.3.4 "
            "attempted to login with the wrong password "
            "(ongoing_password_failure_count=1)."
        )
        self.validate_log_entry_recorded(
            time_before=time_before,
            app_user_oid=user.oid,
            tag=LogEntryTag.wrong_password,
            text=expected_text,
            usecase_tag=LoginToSystem.USECASE_TAG,
        )

    def test_fail_count_increments_on_wrong_password(self):
        user_before = self.create_user_with_two_password_failures()
        login_to_system = LoginToSystem(self.services)
        login_to_system.run(
            user_before.username, "wrong_password", GOOD_IP_ADDRESS
        )
        user_after = self.db.get_app_user_by_username(user_before.username)
        assert user_after.ongoing_password_failure_count == 3

    def create_user_with_two_password_failures(
        self, username=GOOD_USER_USERNAME, password=GOOD_USER_PASSWORD
    ):
        user = self.create_user(username, password)
        user.ongoing_password_failure_count = 2
        two_minutes_ago = datetime.now() - timedelta(minutes=2)
        user.last_password_failure_time = two_minutes_ago
        self.db.add_app_user(user)
        return user

    def test_third_wrong_password_occurrence_logs(self, caplog):
        self.create_user_with_two_password_failures(
            "mrunhappy", GOOD_USER_PASSWORD
        )
        login_to_system = LoginToSystem(self.services)
        login_to_system.run("mrunhappy", "wrong_password", "1.2.3.4")
        self.validate_log_entry(
            caplog,
            "App user (username=mrunhappy) from 1.2.3.4 attempted "
            "to login with the wrong password "
            "(ongoing_password_failure_count=3).",
        )

    def test_password_fail_time_set_on_wrong_password(self):
        self.create_good_user()
        login_to_system = LoginToSystem(self.services)
        time_before_attempt = datetime.now() - timedelta(seconds=1)
        login_to_system.run(
            GOOD_USER_USERNAME, "wrong_password", GOOD_IP_ADDRESS
        )
        time_after_attempt = datetime.now()
        user_after = self.db.get_app_user_by_username(GOOD_USER_USERNAME)
        assert user_after.last_password_failure_time > time_before_attempt
        assert user_after.last_password_failure_time < time_after_attempt

    def test_user_record_changes_on_wrong_password(self):
        user_before = self.create_user_with_two_password_failures()
        login_to_system = LoginToSystem(self.services)
        login_to_system.run(
            user_before.username, "wrong_password", GOOD_IP_ADDRESS
        )
        self.db.rollback()
        user_after = self.db.get_app_user_by_username(user_before.username)
        assert user_after != user_before

    def test_user_locks_on_consecutive_password_failures(self):
        user = self.create_user_and_trip_login_fail_threshold()
        assert user.is_locked

    def create_user_and_trip_login_fail_threshold(self):
        self.create_good_user()
        rules = self.db.get_rules()
        login_to_system = LoginToSystem(self.services)
        for _ in range(rules.login_fail_threshold_count + 1):
            login_to_system.run(
                GOOD_USER_USERNAME, "wrong_password", GOOD_IP_ADDRESS
            )

        return self.db.get_app_user_by_username(GOOD_USER_USERNAME)
