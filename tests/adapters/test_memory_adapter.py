import pytest

from shrike.adapters.memory_adapter import MemoryAdapter
from shrike.entities.app_user import AppUser
from shrike.entities.storage_provider import StorageProvider

storage_provider2 = None

class TestMemoryAdapter:

    storage_provider = None

    @classmethod
    def setup_class(cls):
        cls.storage_provider = cls.get_storage_provider()
        cls.storage_provider.open()
    
    @staticmethod
    def get_storage_provider():
        return MemoryAdapter()

    @classmethod
    def teardown_class(cls):
        cls.storage_provider.close()
        cls.storage_provider = None


    #region - test general properties

    def test_is_a_storage_provider(self):
        assert isinstance(self.storage_provider, StorageProvider)

    def test_get_version_returns_provider_info(self):
        assert self.storage_provider.get_version().startswith(self.storage_provider.VERSION_PREFIX)

    def test_raises_when_not_opened_first(self):
        storage_provider = self.get_storage_provider()
        with pytest.raises(Exception) as excinfo:
            storage_provider.get_version()
        assert str(excinfo.value) == "get_version is not available since the connection is closed"

    def test_raises_when_already_opened(self):
        storage_provider = self.get_storage_provider()
        storage_provider.open()
        with pytest.raises(Exception) as excinfo:
            storage_provider.open()
        assert str(excinfo.value) == "connection already open"

    def test_raises_when_already_closed(self):
        storage_provider = self.get_storage_provider()
        storage_provider.open()
        storage_provider.close()
        with pytest.raises(Exception):
            storage_provider.get_version()

    #endregion


    #region - test transaction handling

    def test_commit_can_be_called_after_no_action(self):
        self.storage_provider.commit()
        self.storage_provider.commit()

    def test_rollback_can_be_called_after_no_action(self):
        self.storage_provider.rollback()
        self.storage_provider.rollback()

    #endregion


    #region - test get next ID methods

    def test_get_next_app_user_id_positive(self):
        next_id = self.storage_provider.get_next_app_user_id()
        assert next_id > 0
 
    def test_get_next_app_user_id_increments(self):
        id1 = self.storage_provider.get_next_app_user_id()
        id2 = self.storage_provider.get_next_app_user_id()
        assert id2 == id1 + 1

    def test_get_next_app_user_id_doesnt_rollback(self):
        self.storage_provider.commit()
        id1 = self.storage_provider.get_next_app_user_id()
        self.storage_provider.rollback()
        id2 = self.storage_provider.get_next_app_user_id()
        assert id2 > id1

    #endregion


    #region - test app_user methods

    def test_get_unknown_raises(self):
        with pytest.raises(KeyError, match='app_user .username=xyz. does not exist'):
            self.storage_provider.get_app_user('xyz')

    def test_get_gets_record(self):
        original_user = self.add_test_app_user('getGETS')
        stored_user = self.storage_provider.get_app_user('getGETS')
        assert stored_user == original_user

    def add_test_app_user(self, username):
        name = 'The ' + username
        password_hash = 'xxx' + username + 'YYY'
        app_user = AppUser(username, name, password_hash)
        oid = self.storage_provider.get_next_app_user_id()
        app_user.oid = oid
        self.storage_provider.add_app_user(app_user)
        return app_user

    def test_get_returns_a_copy(self):
        self.add_test_app_user('getRETURNS')
        copied_user = self.storage_provider.get_app_user('getRETURNS')
        copied_user.name = 'Different'
        stored_user = self.storage_provider.get_app_user('getRETURNS')
        assert stored_user != copied_user

    def test_add_adds_record(self):
        original_user = self.add_test_app_user('addADDS')
        stored_user = self.storage_provider.get_app_user('addADDS')
        assert stored_user == original_user

    def test_add_adds_a_copy(self):
        some_user = self.add_test_app_user('addsCOPY')
        some_user.name = 'Different'
        stored_user = self.storage_provider.get_app_user('addsCOPY')
        assert stored_user != some_user

    def test_add_duplicate_raises(self):
        some_user = self.add_test_app_user('addDUPE')
        with pytest.raises(ValueError, match='app_user .username=addDUPE. already exists'):
            self.storage_provider.add_app_user(some_user)

    def test_update_updates_record(self):
        some_user = self.add_test_app_user('updateUpdates')
        some_user.name = "DIFFERENT"
        self.storage_provider.update_app_user(some_user)
        stored_user = self.storage_provider.get_app_user('updateUpdates')
        assert stored_user == some_user

    def test_exists_true_for_known(self):
        self.add_test_app_user('existsTRUE')
        assert self.storage_provider.exists_app_user('existsTRUE')

    def test_exists_false_for_unknown(self):
        assert self.storage_provider.exists_app_user('existsUNKNOWN') is False

    def test_add_exists_after_commit(self):
        self.add_test_app_user('commitWORKS')
        self.storage_provider.commit()
        assert self.storage_provider.exists_app_user('commitWORKS')

    def test_add_gone_after_rollback(self):
        self.add_test_app_user('rollbackWORKS')
        self.storage_provider.rollback()
        assert not self.storage_provider.exists_app_user('rollbackWORKS')

    #endregion
