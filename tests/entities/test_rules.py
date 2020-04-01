import pytest

from shrike.entities.rules import Rules


class TestRules:

    def test_can_be_instantiated(self):
        Rules()

    def test_has_expected_default_values(self):
        rules = Rules()
        assert rules.login_fail_threshold_count == 3
        assert rules.login_fail_lock_minutes == 15

    def test_equals(self):
        rules_a = Rules()
        rules_b = Rules()
        assert rules_a == rules_b

    @pytest.mark.parametrize(
        ('attr_name', 'attr_value'),
        (
            ('login_fail_threshold_count', -1),
            ('login_fail_lock_minutes', -1),
        )
    )
    def test_not_equals_when_attribute_differs(self, attr_name, attr_value):
        rules_a = Rules()
        rules_b = Rules()
        setattr(rules_b, attr_name, attr_value)
        assert rules_a != rules_b

    def test_not_equals_when_object_differs(self):
        class FakeRules:
            def __init__(self):
                real = Rules()
                self.login_fail_threshold_count = (
                    real.login_fail_threshold_count
                )
                self.login_fail_lock_minutes = (
                    real.login_fail_lock_minutes
                )

        rules_a = Rules()
        rules_b = FakeRules()
        assert rules_a != rules_b
