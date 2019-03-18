import pytest

from shrike.adapters.memory_adapter import MemoryAdapter
from shrike.entities.app_user import AppUser
from shrike.entities.storage_provider import StorageProvider

from tests.entities.test_app_user import TEST_USER


@pytest.fixture
def storage_provider(scope="class"):
    provider = MemoryAdapter()
    provider.add_app_user(TEST_USER)
    return provider


class TestGeneralProperties:

    def test_is_a_storage_provider(self, storage_provider):
        assert isinstance(storage_provider, StorageProvider)


class TestAppUserMethods:

    def test_get_unknown_raises(self, storage_provider):
        with pytest.raises(KeyError, match='app_user .username=xyz. does not exist'):
            storage_provider.get_app_user('xyz')

    def test_get_known_returns_record(self, storage_provider):
        user = storage_provider.get_app_user(TEST_USER.username)
        assert user == TEST_USER

    def test_add_adds_record(self, storage_provider):
        original_user = AppUser('addTest', 'Mr. Add Test', TEST_USER.password_hash)
        storage_provider.add_app_user(original_user)
        stored_user = storage_provider.get_app_user('addTest')
        assert stored_user == original_user

    def test_add_duplicate_raises(self, storage_provider):
        with pytest.raises(ValueError, match='app_user .username=' + TEST_USER.username + '. already exists'):
            storage_provider.add_app_user(TEST_USER)
