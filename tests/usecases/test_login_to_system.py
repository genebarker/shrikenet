from datetime import datetime, timedelta, timezone
import logging

import pytest

from shrike.adapters.memory_adapter import MemoryAdapter
from shrike.adapters.swapcase_adapter import SwapcaseAdapter
from shrike.entities.app_user import AppUser
from shrike.entities.constants import Constants
from shrike.entities.services import Services
from shrike.usecases.login_to_system import LoginToSystem
from shrike.usecases.login_to_system_result import LoginToSystemResult

GOOD_USER_USERNAME = 'fmulder'
GOOD_USER_PASSWORD = 'scully'
GOOD_IP_ADDRESS = '1.2.3.4'
MODULE_UNDER_TEST = 'shrike.usecases.login_to_system'


logging.basicConfig(level=logging.DEBUG)


class SetupClass:

    def setup_method(self, method):
        self.db = MemoryAdapter()
        self.db.open()
        text_transformer = None
        self.crypto = SwapcaseAdapter()
        self.services = Services(self.db, text_transformer, self.crypto)

    def teardown_method(self, method):
        self.db.close()

    def create_good_user(self):
        return self.create_and_store_user(GOOD_USER_USERNAME,
                                          GOOD_USER_PASSWORD)

    def create_and_store_user(self, username, password):
        user = self.create_user(username, password)
        self.db.add_app_user(user)
        self.db.commit()
        return user

    def create_user(self, username, password):
        oid = self.db.get_next_app_user_oid()
        name = 'mr ' + username
        password_hash = self.crypto.generate_hash_from_string(password)
        user = AppUser(oid, username, name, password_hash)
        return user

    def validate_login_fails(self, username, password,
                             message='Login attempt failed.'):
        login_to_system = LoginToSystem(self.services)
        result = login_to_system.run(username, password, GOOD_IP_ADDRESS)
        assert result.has_failed
        assert not result.must_change_password
        assert result.message == message

    def validate_log_entry(self, caplog, message):
        assert len(caplog.records) == 1
        log_record = caplog.records[0]
        assert log_record.levelname == 'INFO'
        assert log_record.name == MODULE_UNDER_TEST
        assert log_record.message == message

    def validate_successful_result(self, user, login_result,
                                   expected_login_message):
        assert login_result.user_oid == user.oid
        assert not login_result.has_failed
        assert not login_result.must_change_password
        assert login_result.message.startswith(expected_login_message)


class TestUnknownUserPaths(SetupClass):

    def test_login_fails_on_unknown_username(self):
        self.validate_login_fails('unknown_username', 'some password')

    def test_unknown_username_occurrence_logged(self, caplog):
        login_to_system = LoginToSystem(self.services)
        login_to_system.run('mrunknown', None, '10.11.12.13')
        self.validate_log_entry(
            caplog,
            'Unknown app user (username=mrunknown) from 10.11.12.13 '
            'attempted to login.'
        )


class TestWrongPasswordPaths(SetupClass):

    def test_login_fails_on_wrong_password(self):
        self.create_good_user()
        self.validate_login_fails(GOOD_USER_USERNAME, 'wrong_password')

    def test_wrong_password_occurrence_logs(self, caplog):
        self.create_and_store_user('mrunhappy', GOOD_USER_PASSWORD)
        login_to_system = LoginToSystem(self.services)
        login_to_system.run('mrunhappy', 'wrong_password', '1.2.3.4')
        self.validate_log_entry(
            caplog,
            'App user (username=mrunhappy) from 1.2.3.4 attempted '
            'to login with the wrong password '
            '(ongoing_password_failure_count=1).'
        )

    def test_fail_count_increments_on_wrong_password(self):
        user_before = self.create_user_with_two_password_failures()
        login_to_system = LoginToSystem(self.services)
        login_to_system.run(user_before.username, 'wrong_password',
                            GOOD_IP_ADDRESS)
        user_after = self.db.get_app_user_by_username(user_before.username)
        assert user_after.ongoing_password_failure_count == 3

    def create_user_with_two_password_failures(self,
                                               username=GOOD_USER_USERNAME,
                                               password=GOOD_USER_PASSWORD):
        user = self.create_user(username, password)
        user.ongoing_password_failure_count = 2
        two_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=2)
        user.last_password_failure_time = two_minutes_ago
        self.db.add_app_user(user)
        return user

    def test_third_wrong_password_occurrence_logs(self, caplog):
        self.create_user_with_two_password_failures('mrunhappy',
                                                    GOOD_USER_PASSWORD)
        login_to_system = LoginToSystem(self.services)
        login_to_system.run('mrunhappy', 'wrong_password', '1.2.3.4')
        self.validate_log_entry(
            caplog,
            'App user (username=mrunhappy) from 1.2.3.4 attempted '
            'to login with the wrong password '
            '(ongoing_password_failure_count=3).'
        )

    def test_password_fail_time_set_on_wrong_password(self):
        self.create_good_user()
        login_to_system = LoginToSystem(self.services)
        time_before_attempt = datetime.now(timezone.utc)
        login_to_system.run(GOOD_USER_USERNAME, 'wrong_password',
                            GOOD_IP_ADDRESS)
        time_after_attempt = datetime.now(timezone.utc)
        user_after = self.db.get_app_user_by_username(GOOD_USER_USERNAME)
        assert user_after.last_password_failure_time > time_before_attempt
        assert user_after.last_password_failure_time < time_after_attempt

    def test_user_record_changes_on_wrong_password(self):
        user_before = self.create_user_with_two_password_failures()
        login_to_system = LoginToSystem(self.services)
        login_to_system.run(user_before.username, 'wrong_password',
                            GOOD_IP_ADDRESS)
        self.db.rollback()
        user_after = self.db.get_app_user_by_username(user_before.username)
        assert user_after != user_before

    def test_user_locks_on_consecutive_password_failures(self):
        self.create_good_user()
        login_to_system = LoginToSystem(self.services)
        for _ in range(Constants.LOGIN_FAIL_THRESHOLD_COUNT + 1):
            login_to_system.run(GOOD_USER_USERNAME, 'wrong_password',
                                GOOD_IP_ADDRESS)

        user = self.db.get_app_user_by_username(GOOD_USER_USERNAME)
        assert user.is_locked


class TestGoodCredentialPaths(SetupClass):

    def test_login_succeeds_for_good_credentials(self):
        good_user = self.create_good_user()
        login_to_system = LoginToSystem(self.services)
        result = login_to_system.run(GOOD_USER_USERNAME, GOOD_USER_PASSWORD,
                                     GOOD_IP_ADDRESS)
        self.validate_successful_result(good_user, result,
                                        'Login successful.')

    def test_successful_login_logs(self, caplog):
        self.create_and_store_user('joe', 'some_password')
        login_to_system = LoginToSystem(self.services)
        login_to_system.run('joe', 'some_password', '4.3.2.1')
        self.validate_log_entry(
            caplog,
            'App user (username=joe) from 4.3.2.1 successfully logged in.'
        )

    def test_password_fail_count_reset_on_successful_login(self):
        user = self.create_good_user()
        user.ongoing_password_failure_count = 2
        self.db.update_app_user(user)
        login_to_system = LoginToSystem(self.services)
        login_to_system.run(GOOD_USER_USERNAME, GOOD_USER_PASSWORD,
                            GOOD_IP_ADDRESS)
        user_after = self.db.get_app_user_by_username(GOOD_USER_USERNAME)
        assert user_after.ongoing_password_failure_count == 0


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


class TestLockedUserPaths(SetupClass):

    def test_login_fails_when_user_locked(self):
        self.create_locked_user()
        self.validate_login_fails(
            GOOD_USER_USERNAME, GOOD_USER_PASSWORD,
            message='Login attempt failed. Your account is locked.'
        )

    def create_locked_user(self, lock_time=datetime.now(timezone.utc)):
        user = self.create_user(GOOD_USER_USERNAME, GOOD_USER_PASSWORD)
        user.is_locked = True
        user.last_password_failure_time = lock_time
        self.db.add_app_user(user)
        return user

    def test_lock_checked_before_password(self):
        self.create_locked_user()
        self.validate_login_fails(
            GOOD_USER_USERNAME, 'wrong_password',
            message='Login attempt failed. Your account is locked.'
        )

    def test_can_login_after_lock_length_met(self):
        self.create_user_with_expired_lock()
        login_to_system = LoginToSystem(self.services)
        result = login_to_system.run(GOOD_USER_USERNAME, GOOD_USER_PASSWORD,
                                     GOOD_IP_ADDRESS)
        assert not result.has_failed

    def create_user_with_expired_lock(self):
        lock_time = (datetime.now(timezone.utc)
                     - timedelta(minutes=Constants.LOGIN_FAIL_LOCK_MINUTES))
        return self.create_locked_user(lock_time)

    def test_unlocks_on_good_password_after_lock_length_met(self):
        self.create_user_with_expired_lock()
        login_to_system = LoginToSystem(self.services)
        login_to_system.run(GOOD_USER_USERNAME, GOOD_USER_PASSWORD,
                            GOOD_IP_ADDRESS)
        user = self.db.get_app_user_by_username(GOOD_USER_USERNAME)
        assert not user.is_locked


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
