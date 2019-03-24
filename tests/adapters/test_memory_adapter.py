import pytest

from shrike.adapters.memory_adapter import MemoryAdapter
from shrike.entities.app_user import AppUser
from shrike.entities.storage_provider import StorageProvider

storage_provider2 = None

class TestMemoryAdapter:

    storage_provider = None

    @classmethod
    def setup_class(cls):
        cls.storage_provider = MemoryAdapter()

    @classmethod
    def teardown_class(cls):
        cls.storage_provider = None


    # test general properties

    def test_is_a_storage_provider(self):
        assert isinstance(self.storage_provider, StorageProvider)


    # test app_user methods

    def test_get_unknown_raises(self):
        with pytest.raises(KeyError, match='app_user .username=xyz. does not exist'):
            self.storage_provider.get_app_user('xyz')

    def test_get_gets_record(self):
        original_user = self.create_test_app_user('getGETS')
        self.storage_provider.add_app_user(original_user)
        stored_user = self.storage_provider.get_app_user('getGETS')
        assert stored_user == original_user

    @staticmethod
    def create_test_app_user(username):
        name = 'The ' + username
        password_hash = 'xxx' + username + 'YYY'
        app_user = AppUser(username, name, password_hash)
        return app_user

    def test_get_returns_a_copy(self):
        original_user = self.create_test_app_user('getRETURNS')
        self.storage_provider.add_app_user(original_user)

        copied_user = self.storage_provider.get_app_user('getRETURNS')
        copied_user.name = 'Different'
        stored_user = self.storage_provider.get_app_user('getRETURNS')
        assert stored_user != copied_user

    def test_add_adds_record(self):
        original_user = self.create_test_app_user('addADDS')
        self.storage_provider.add_app_user(original_user)
        stored_user = self.storage_provider.get_app_user('addADDS')
        assert stored_user == original_user

    def test_add_adds_a_copy(self):
        some_user = self.create_test_app_user('addsCOPY')
        self.storage_provider.add_app_user(some_user)
        some_user.name = 'Different'
        stored_user = self.storage_provider.get_app_user('addsCOPY')
        assert stored_user != some_user

    def test_add_duplicate_raises(self):
        some_user = self.create_test_app_user('addDUPE')
        self.storage_provider.add_app_user(some_user)
        with pytest.raises(ValueError, match='app_user .username=addDUPE. already exists'):
            self.storage_provider.add_app_user(some_user)

    def test_exists_true_for_known(self):
        some_user = self.create_test_app_user('existsTRUE')
        self.storage_provider.add_app_user(some_user)
        assert self.storage_provider.exists_app_user('existsTRUE')

    def test_exists_false_for_unknown(self):
        assert self.storage_provider.exists_app_user('existsUNKNOWN') is False
