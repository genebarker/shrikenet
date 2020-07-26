from datetime import datetime, timezone

import pytest

from shrikenet.entities.event_tag import EventTag
from shrikenet.usecases.login_to_system import LoginToSystem
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

    def test_unknown_username_occurrence_recorded(self):
        time_before = datetime.now(timezone.utc)
        login_to_system = LoginToSystem(self.services)
        login_to_system.run('mrunknown', None, '10.11.12.13')
        expected_text = ('Unknown app user (username=mrunknown) from '
                         '10.11.12.13 attempted to login.')
        self.validate_event_recorded(
            time_before=time_before,
            app_user_oid=None,
            tag=EventTag.unknown_user,
            text=expected_text,
            usecase_tag=LoginToSystem.USECASE_TAG
        )
