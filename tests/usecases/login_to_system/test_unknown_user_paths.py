import pytest

from shrike.usecases.login_to_system import LoginToSystem
from tests.usecases.login_to_system.setup_class import SetupClass


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
