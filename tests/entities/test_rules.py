import pytest

from shrike.entities.rules import Rules


class TestRules:

    def test_can_be_instantiated(self):
        Rules()

    def test_has_expected_default_values(self):
        rules = Rules()
        assert rules.login_fail_threshold_count == 3
        assert rules.login_fail_lock_minutes == 15
