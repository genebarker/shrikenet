from datetime import datetime, timezone

import pytest

from shrikenet.usecases.login_to_system import LoginToSystem
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

    def create_dormant_user(self, username=GOOD_USER_USERNAME,
                            password=GOOD_USER_PASSWORD):
        user = self.create_user(username, password)
        user.is_dormant = True
        self.db.add_app_user(user)
        return user

    def test_dormant_checked_before_password(self):
        self.create_dormant_user()
        self.validate_login_fails(
            GOOD_USER_USERNAME, 'wrong_password',
            message='Login attempt failed. Your credentials are invalid.'
        )

    def test_dormant_user_login_attempt_logs(self, caplog):
        self.create_dormant_user('max', 'some_password')
        login_to_system = LoginToSystem(self.services)
        login_to_system.run('max', 'some_password', '9.8.7.6')
        self.validate_log_entry(
            caplog,
            'Dormant app user (username=max) from 9.8.7.6 attempted to '
            'login.'
        )

    def test_dormant_user_login_attempt_recorded(self):
        user = self.create_dormant_user('max', 'some_password')
        time_before = datetime.now(timezone.utc)
        login_to_system = LoginToSystem(self.services)
        login_to_system.run('max', 'some_password', '4.5.6.7')
        event = self.db.get_last_event()
        assert event.time > time_before
        assert event.time < datetime.now(timezone.utc)
        assert event.app_user_oid == user.oid
        assert event.tag == 'dormant_user'
        assert event.text == ('Dormant app user (username=max) from 4.5.6.7 '
                              'attempted to login.')
        assert event.usecase_tag == 'login_to_system'
