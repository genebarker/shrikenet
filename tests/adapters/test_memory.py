import copy
from datetime import datetime, timezone
from operator import attrgetter

import pytest

from shrikenet.adapters.memory import Memory
from shrikenet.entities.rules import Rules


class TestMemory:

    @staticmethod
    def get_storage_provider():
        return Memory()

    @pytest.fixture
    def storage_provider(self):
        provider = self.get_storage_provider()
        provider.open()
        yield provider
        provider.close()

    # region - test get / save rules

    def test_get_rules_returns_rules_object(self, storage_provider):
        rules = storage_provider.get_rules()
        assert isinstance(rules, Rules)

    def test_initial_rules_are_set_to_defaults(self, storage_provider):
        rules = storage_provider.get_rules()
        default_rules = Rules()
        assert rules == default_rules

    def test_save_rules_saves_them(self, storage_provider):
        rules_a = self.create_and_store_sample_rules(storage_provider)
        rules_b = storage_provider.get_rules()
        assert rules_a == rules_b

    def create_and_store_sample_rules(self, storage_provider):
        rules = self.create_sample_rules()
        storage_provider.save_rules(rules)
        return rules

    def create_sample_rules(self):
        rules = Rules()
        rules.login_fail_threshold_count = 42
        return rules

    def test_get_rules_returns_a_copy(self, storage_provider):
        rules = self.create_and_store_sample_rules(storage_provider)
        rules.login_fail_threshold_count += 1
        assert (
            self.create_sample_rules()
            == storage_provider.get_rules()
        )

    def test_rules_exist_after_commit(self, storage_provider):
        rules = self.create_and_store_sample_rules(storage_provider)
        storage_provider.commit()
        assert rules == storage_provider.get_rules()

    def test_rules_gone_after_rollback(self, storage_provider):
        rules = self.create_and_store_sample_rules(storage_provider)
        storage_provider.commit()
        rules.login_fail_threshold_count = 99
        storage_provider.save_rules(rules)
        storage_provider.rollback()
        assert (
            self.create_sample_rules()
            == storage_provider.get_rules()
        )

    # endregion
