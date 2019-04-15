import pytest

from shrike.adapters.memory_adapter import MemoryAdapter
from shrike.entities.app_user import AppUser
from shrike.entities.storage_provider import StorageProvider

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

    def test_get_next_app_user_oid_positive(self):
        next_oid = self.storage_provider.get_next_app_user_oid()
        assert next_oid > 0
 
    def test_get_next_app_user_oid_increments(self):
        oid1 = self.storage_provider.get_next_app_user_oid()
        oid2 = self.storage_provider.get_next_app_user_oid()
        assert oid2 == oid1 + 1

    def test_get_next_app_user_oid_doesnt_rollback(self):
        self.storage_provider.commit()
        oid1 = self.storage_provider.get_next_app_user_oid()
        self.storage_provider.rollback()
        oid2 = self.storage_provider.get_next_app_user_oid()
        assert oid2 > oid1

    #endregion


    #region - test app_user methods

    def test_get_app_user_by_username_unknown_raises(self):
        with pytest.raises(KeyError, match='app_user .username=xyz. does not exist'):
            self.storage_provider.get_app_user_by_username('xyz')

    def test_get_app_user_by_username_gets_record(self):
        original_user = self.add_test_app_user('getAppUserGETS')
        stored_user = self.storage_provider.get_app_user_by_username('getAppUserGETS')
        assert stored_user == original_user

    def add_test_app_user(self, username):
        name = 'The ' + username
        password_hash = 'xxx' + username + 'YYY'
        app_user = AppUser(username, name, password_hash)
        oid = self.storage_provider.get_next_app_user_oid()
        app_user.oid = oid
        self.storage_provider.add_app_user(app_user)
        return app_user

    def test_get_app_user_by_oid_gets_record(self):
        original_user = self.add_test_app_user('getAppUserByOIDGETS')
        stored_user = self.storage_provider.get_app_user_by_oid(original_user.oid)
        assert stored_user == original_user

    def test_get_app_user_by_oid_unknown_raises(self):
        with pytest.raises(KeyError, match='app_user .oid=12345. does not exist'):
            self.storage_provider.get_app_user_by_oid('12345')

    def test_get_app_user_returns_a_copy(self):
        self.add_test_app_user('getAppUserRETURNS')
        copied_user = self.storage_provider.get_app_user_by_username('getAppUserRETURNS')
        copied_user.name = 'Different'
        stored_user = self.storage_provider.get_app_user_by_username('getAppUserRETURNS')
        assert stored_user != copied_user

    def test_add_app_user_adds_record(self):
        original_user = self.add_test_app_user('addAppUserADDS')
        stored_user = self.storage_provider.get_app_user_by_username('addAppUserADDS')
        assert stored_user == original_user

    def test_add_app_user_adds_a_copy(self):
        some_user = self.add_test_app_user('addAppUserAddsCOPY')
        some_user.name = 'Different'
        stored_user = self.storage_provider.get_app_user_by_username('addAppUserAddsCOPY')
        assert stored_user != some_user

    def test_add_app_user_with_duplicate_username_raises(self):
        some_user = self.add_test_app_user('addAppUserDupeUsername')
        with pytest.raises(ValueError, match='app_user .username=addAppUserDupeUsername. already exists'):
            self.storage_provider.add_app_user(some_user)

    def test_add_app_user_with_duplicate_oid_raises(self):
        some_user = self.add_test_app_user('addAppUserDupeOID')
        with pytest.raises(ValueError, match='app_user .oid={0}. already exists'.format(some_user.oid)):
            some_user.username = 'Different'
            self.storage_provider.add_app_user(some_user)

    def test_update_app_user_updates_record(self):
        some_user = self.add_test_app_user('updateAppUserUpdates')
        some_user.name = 'Differnt'
        self.storage_provider.update_app_user(some_user)
        stored_user = self.storage_provider.get_app_user_by_username('updateAppUserUpdates')
        assert stored_user == some_user

    def test_update_app_user_updates_a_copy(self):
        some_user = self.add_test_app_user('updateAppUserUpdatesCopy')
        some_user.name = 'Different'
        self.storage_provider.update_app_user(some_user)
        some_user.name = 'Very Different'
        stored_user = self.storage_provider.get_app_user_by_username('updateAppUserUpdatesCopy')
        assert stored_user != some_user

    def test_exists_app_user_true_for_known(self):
        self.add_test_app_user('existsAppUserTRUE')
        assert self.storage_provider.exists_app_username('existsAppUserTRUE')

    def test_exists_app_user_false_for_unknown(self):
        assert self.storage_provider.exists_app_username('existsAppUserUNKNOWN') is False

    def test_add_app_user_record_exists_after_commit(self):
        self.add_test_app_user('commitAppUserWORKS')
        self.storage_provider.commit()
        assert self.storage_provider.exists_app_username('commitAppUserWORKS')

    def test_add_app_user_record_gone_after_rollback(self):
        self.add_test_app_user('rollbackAppUserWORKS')
        self.storage_provider.rollback()
        assert not self.storage_provider.exists_app_username('rollbackAppUserWORKS')

    #endregion
