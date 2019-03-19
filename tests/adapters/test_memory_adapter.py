import pytest

from shrike.adapters.memory_adapter import MemoryAdapter
from shrike.entities.app_user import AppUser
from shrike.entities.storage_provider import StorageProvider


@pytest.fixture
def storage_provider(scope="class"):
    provider = MemoryAdapter()
    return provider


class TestGeneralProperties:

    def test_is_a_storage_provider(self, storage_provider):
        assert isinstance(storage_provider, StorageProvider)


class TestAppUserMethods:

    def test_get_unknown_raises(self, storage_provider):
        with pytest.raises(KeyError, match='app_user .username=xyz. does not exist'):
            storage_provider.get_app_user('xyz')

    def test_get_gets_record(self, storage_provider):
        original_user = self.create_test_app_user('getGETS')
        storage_provider.add_app_user(original_user)
        stored_user = storage_provider.get_app_user('getGETS')
        assert stored_user == original_user

    @staticmethod
    def create_test_app_user(username):
        name = 'The ' + username
        password_hash = 'xxx' + username + 'YYY'
        app_user = AppUser(username, name, password_hash)
        return app_user

    def test_get_returns_a_copy(self, storage_provider):
        original_user = self.create_test_app_user('getRETURNS')
        storage_provider.add_app_user(original_user)

        copied_user = storage_provider.get_app_user('getRETURNS')
        copied_user.name = 'Different'
        stored_user = storage_provider.get_app_user('getRETURNS')
        assert stored_user != copied_user

    def test_add_adds_record(self, storage_provider):
        original_user = self.create_test_app_user('addADDS')
        storage_provider.add_app_user(original_user)
        stored_user = storage_provider.get_app_user('addADDS')
        assert stored_user == original_user

    def test_add_adds_a_copy(self, storage_provider):
        some_user = self.create_test_app_user('addsCOPY')
        storage_provider.add_app_user(some_user)
        some_user.name = 'Different'
        stored_user = storage_provider.get_app_user('addsCOPY')
        assert stored_user != some_user

    def test_add_duplicate_raises(self, storage_provider):
        some_user = self.create_test_app_user('addDUPE')
        storage_provider.add_app_user(some_user)
        with pytest.raises(ValueError, match='app_user .username=addDUPE. already exists'):
            storage_provider.add_app_user(some_user)

    def test_exists_true_for_known(self, storage_provider):
        some_user = self.create_test_app_user('existsTRUE')
        storage_provider.add_app_user(some_user)
        assert storage_provider.exists_app_user('existsTRUE')

    def test_exists_false_for_unknown(self, storage_provider):
        assert storage_provider.exists_app_user('existsUNKNOWN') is False
