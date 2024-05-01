from datetime import datetime, timedelta

from shrikenet.entities.log_entry_tag import LogEntryTag
from shrikenet.usecases.login_to_system import LoginToSystem
from tests.usecases.login_to_system.setup_class import (
    SetupClass,
    GOOD_USER_USERNAME,
    GOOD_USER_PASSWORD,
    GOOD_IP_ADDRESS,
)


class TestLockedUserPaths(SetupClass):

    def test_login_fails_when_user_locked(self):
        self.create_locked_user()
        self.validate_login_fails(
            GOOD_USER_USERNAME,
            GOOD_USER_PASSWORD,
            message="Login attempt failed. Your account is locked.",
        )

    def create_locked_user(
        self,
        lock_time=datetime.now(),
        username=GOOD_USER_USERNAME,
        password=GOOD_USER_PASSWORD,
    ):
        user = self.create_user(username, password)
        user.is_locked = True
        user.last_password_failure_time = lock_time
        user.oid = self.db.add_app_user(user)
        return user

    def test_lock_checked_before_password(self):
        self.create_locked_user()
        self.validate_login_fails(
            GOOD_USER_USERNAME,
            "wrong_password",
            message="Login attempt failed. Your account is locked.",
        )

    def test_locked_user_login_attempt_logs(self, caplog):
        self.create_locked_user(username="fred", password="some_password")
        login_to_system = LoginToSystem(self.services)
        login_to_system.run("fred", "some_password", "8.7.6.5")
        self.validate_log_entry(
            caplog,
            "Locked app user (username=fred) from 8.7.6.5 attempted to "
            "login.",
        )

    def test_locked_user_login_attempt_recorded(self):
        user = self.create_locked_user(
            username="jill", password="some_password"
        )
        time_before = datetime.now() - timedelta(seconds=1)
        login_to_system = LoginToSystem(self.services)
        login_to_system.run("jill", "some_password", "4.5.6.7")
        expected_text = (
            "Locked app user (username=jill) from 4.5.6.7 "
            "attempted to login."
        )
        self.validate_log_entry_recorded(
            time_before=time_before,
            app_user_oid=user.oid,
            tag=LogEntryTag.locked_user,
            text=expected_text,
            usecase_tag="login_to_system",
        )

    def test_can_login_after_lock_length_met(self):
        result = self.perform_login_after_lock_expires()
        assert not result.has_failed

    def perform_login_after_lock_expires(self):
        self.create_user_with_expired_lock()
        login_to_system = LoginToSystem(self.services)
        return login_to_system.run(
            GOOD_USER_USERNAME, GOOD_USER_PASSWORD, GOOD_IP_ADDRESS
        )

    def create_user_with_expired_lock(self):
        rules = self.db.get_rules()
        lock_time = datetime.now() - timedelta(
            minutes=rules.login_fail_lock_minutes
        )
        return self.create_locked_user(lock_time)

    def test_unlocks_on_good_password_after_lock_length_met(self):
        self.perform_login_after_lock_expires()
        user = self.db.get_app_user_by_username(GOOD_USER_USERNAME)
        assert not user.is_locked
