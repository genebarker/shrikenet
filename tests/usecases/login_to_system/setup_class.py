from datetime import datetime, timedelta, timezone
import logging

import pytest

from shrike.adapters.memory_adapter import MemoryAdapter
from shrike.adapters.swapcase_adapter import SwapcaseAdapter
from shrike.entities.app_user import AppUser
from shrike.entities.services import Services
from shrike.usecases.login_to_system import LoginToSystem

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
