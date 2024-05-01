from datetime import datetime
import logging

from shrikenet.adapters.sqlite import SQLite
from shrikenet.adapters.swapcase import Swapcase
from shrikenet.entities.app_user import AppUser
from shrikenet.entities.services import Services
from shrikenet.usecases.login_to_system import LoginToSystem

DATABASE = "test.db"

GOOD_USER_USERNAME = "fmulder"
GOOD_USER_PASSWORD = "scully"
GOOD_IP_ADDRESS = "1.2.3.4"
MODULE_UNDER_TEST = "shrikenet.usecases.login_to_system"


logging.basicConfig(level=logging.DEBUG)


class SetupClass:

    def setup_method(self, method):
        self.db = SQLite(DATABASE)
        self.db.open()
        self.db.reset_database_objects()
        text_transformer = None
        self.crypto = Swapcase()
        self.services = Services(self.db, text_transformer, self.crypto)

    def teardown_method(self, method):
        self.db.close()

    def create_good_user(self):
        return self.create_and_store_user(
            GOOD_USER_USERNAME, GOOD_USER_PASSWORD
        )

    def create_and_store_user(self, username, password):
        user = self.create_user(username, password)
        user.oid = self.db.add_app_user(user)
        self.db.commit()
        return user

    def create_user(self, username, password):
        oid = -1
        name = "mr " + username
        password_hash = self.crypto.generate_hash_from_string(password)
        user = AppUser(oid, username, name, password_hash)
        return user

    def validate_login_fails(
        self, username, password, message="Login attempt failed."
    ):
        login_to_system = LoginToSystem(self.services)
        result = login_to_system.run(username, password, GOOD_IP_ADDRESS)
        assert result.has_failed
        assert not result.must_change_password
        assert result.message == message

    def validate_log_entry(self, caplog, message):
        for log_record in caplog.records:
            assert log_record.levelname == "INFO"
            assert log_record.name == MODULE_UNDER_TEST
            assert log_record.message == message

    def validate_log_entry_recorded(
        self, time_before, app_user_oid, tag, text, usecase_tag
    ):
        log_entry = self.db.get_last_log_entry()
        assert log_entry.time > time_before
        assert log_entry.time < datetime.now()
        assert log_entry.app_user_oid == app_user_oid
        assert log_entry.tag == tag
        assert log_entry.text == text
        assert log_entry.usecase_tag == usecase_tag

    def validate_successful_result(
        self, user, login_result, expected_login_message
    ):
        assert login_result.user_oid == user.oid
        assert not login_result.has_failed
        assert not login_result.must_change_password
        assert login_result.message.startswith(expected_login_message)
