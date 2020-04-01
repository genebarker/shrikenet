import pytest

from shrike.entities.record_validator import RecordValidator
from shrike.entities.rules import Rules
from shrike.entities.rules_validator import RulesValidator


class TestGeneralProperties:

    def test_is_a_record_validator(self):
        assert issubclass(RulesValidator, RecordValidator)


class TestFieldValidation:

    def test_successful_validation_returns_none(self):
        rules = Rules()
        assert RulesValidator.validate_fields(rules) is None

    def test_login_fail_threshold_count_required(self):
        rules = Rules()
        rules.login_fail_threshold_count = None
        self.verify_validation_raises(rules)

    @staticmethod
    def verify_validation_raises(rules):
        with pytest.raises(ValueError):
            RulesValidator.validate_fields(rules)

    @pytest.mark.parametrize(('count'), (
        ('not a number'),
        (100.1),
        (0),
    ))
    def test_login_fail_threshold_count_validated(self, count):
        rules = Rules()
        rules.login_fail_threshold_count = count
        self.verify_validation_raises(rules)

    @pytest.mark.parametrize(('minutes'), (
        ('not a number'),
        (100.1),
        (0),
    ))
    def test_login_fail_lock_minutes_validated(self, minutes):
        rules = Rules()
        rules.login_fail_lock_minutes = minutes
        self.verify_validation_raises(rules)
