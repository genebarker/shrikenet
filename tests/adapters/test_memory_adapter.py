from datetime import datetime, timezone

import pytest

from shrike.adapters.memory_adapter import MemoryAdapter
from shrike.entities.app_user import AppUser
from shrike.entities.post import Post
from shrike.entities.storage_provider import StorageProvider

class TestMemoryAdapter:

    @staticmethod
    def get_storage_provider():
        return MemoryAdapter()

    @pytest.fixture(scope='class')
    def storage_provider(self):
        provider = self.get_storage_provider()
        provider.open()
        yield provider
        provider.close()

    #region - test general properties

    def test_is_a_storage_provider(self, storage_provider):
        assert isinstance(storage_provider, StorageProvider)

    def test_get_version_returns_provider_info(self, storage_provider):
        assert storage_provider.get_version().startswith(storage_provider.VERSION_PREFIX)

    def test_raises_when_not_opened_first(self):
        storage_provider = self.get_storage_provider()
        with pytest.raises(Exception) as excinfo:
            storage_provider.get_version()
        assert str(excinfo.value) == 'get_version is not available since the connection is closed'

    def test_raises_when_already_opened(self, storage_provider):
        with pytest.raises(Exception) as excinfo:
            storage_provider.open()
        assert str(excinfo.value) == 'connection already open'

    def test_raises_when_already_closed(self):
        storage_provider = self.get_storage_provider()
        storage_provider.open()
        storage_provider.close()
        with pytest.raises(Exception):
            storage_provider.get_version()

    #endregion


    #region - test transaction handling

    def test_commit_can_be_called_after_no_action(self, storage_provider):
        storage_provider.commit()
        storage_provider.commit()

    def test_rollback_can_be_called_after_no_action(self, storage_provider):
        storage_provider.rollback()
        storage_provider.rollback()

    #endregion


    #region - test get next ID methods

    GET_NEXT_OID_METHODS = ['get_next_app_user_oid', 'get_next_post_oid',]

    @pytest.mark.parametrize('method_name,', GET_NEXT_OID_METHODS)
    def test_get_next_oid_positive(self, storage_provider, method_name):
        get_next_oid = getattr(storage_provider, method_name)
        assert get_next_oid() > 0
 
    @pytest.mark.parametrize('method_name,', GET_NEXT_OID_METHODS)
    def test_get_next_oid_increments(self, storage_provider, method_name):
        get_next_oid = getattr(storage_provider, method_name)
        oid1 = get_next_oid()
        oid2 = get_next_oid()
        assert oid2 == oid1 + 1

    @pytest.mark.parametrize('method_name,', GET_NEXT_OID_METHODS)
    def test_get_next_oid_doesnt_rollback(self, storage_provider, method_name):
        get_next_oid = getattr(storage_provider, method_name)
        storage_provider.commit()
        oid1 = get_next_oid()
        storage_provider.rollback()
        oid2 = get_next_oid()
        assert oid2 > oid1

    #endregion


    #region - test app_user methods

    def test_get_app_user_by_username_unknown_raises(self, storage_provider):
        with pytest.raises(KeyError, match='app_user .username=xyz. does not exist'):
            storage_provider.get_app_user_by_username('xyz')

    def test_get_app_user_by_username_gets_record(self, storage_provider):
        original_user = self.add_test_app_user('getAppUserGETS', storage_provider)
        stored_user = storage_provider.get_app_user_by_username('getAppUserGETS')
        assert stored_user == original_user

    def add_test_app_user(self, username, storage_provider):
        name = 'The ' + username
        password_hash = 'xxx' + username + 'YYY'
        app_user = AppUser(username, name, password_hash)
        oid = storage_provider.get_next_app_user_oid()
        app_user.oid = oid
        storage_provider.add_app_user(app_user)
        return app_user

    def test_get_app_user_by_oid_unknown_raises(self, storage_provider):
        with pytest.raises(KeyError, match='app_user .oid=12345. does not exist'):
            storage_provider.get_app_user_by_oid('12345')

    def test_get_app_user_by_oid_gets_record(self, storage_provider):
        original_user = self.add_test_app_user('getAppUserByOIDGETS', storage_provider)
        stored_user = storage_provider.get_app_user_by_oid(original_user.oid)
        assert stored_user == original_user

    def test_get_app_user_returns_a_copy(self, storage_provider):
        self.add_test_app_user('getAppUserRETURNS', storage_provider)
        copied_user = storage_provider.get_app_user_by_username('getAppUserRETURNS')
        copied_user.name = 'Different'
        stored_user = storage_provider.get_app_user_by_username('getAppUserRETURNS')
        assert stored_user != copied_user

    def test_add_app_user_adds_record(self, storage_provider):
        original_user = self.add_test_app_user('addAppUserADDS', storage_provider)
        stored_user = storage_provider.get_app_user_by_username('addAppUserADDS')
        assert stored_user == original_user

    def test_add_app_user_adds_a_copy(self, storage_provider):
        some_user = self.add_test_app_user('addAppUserAddsCOPY', storage_provider)
        some_user.name = 'Different'
        stored_user = storage_provider.get_app_user_by_username('addAppUserAddsCOPY')
        assert stored_user != some_user

    def test_add_app_user_with_duplicate_username_raises(self, storage_provider):
        some_user = self.add_test_app_user('addAppUserDupeUsername', storage_provider)
        with pytest.raises(ValueError, match='app_user .username=addAppUserDupeUsername. already exists'):
            storage_provider.add_app_user(some_user)

    def test_add_app_user_with_duplicate_oid_raises(self, storage_provider):
        some_user = self.add_test_app_user('addAppUserDupeOID', storage_provider)
        with pytest.raises(ValueError, match='app_user .oid={0}. already exists'.format(some_user.oid)):
            some_user.username = 'Different'
            storage_provider.add_app_user(some_user)

    def test_update_app_user_updates_record(self, storage_provider):
        some_user = self.add_test_app_user('updateAppUserUpdates', storage_provider)
        some_user.name = 'Differnt'
        storage_provider.update_app_user(some_user)
        stored_user = storage_provider.get_app_user_by_username('updateAppUserUpdates')
        assert stored_user == some_user

    def test_update_app_user_updates_a_copy(self, storage_provider):
        some_user = self.add_test_app_user('updateAppUserUpdatesCopy', storage_provider)
        some_user.name = 'Different'
        storage_provider.update_app_user(some_user)
        some_user.name = 'Very Different'
        stored_user = storage_provider.get_app_user_by_username('updateAppUserUpdatesCopy')
        assert stored_user != some_user

    def test_exists_app_user_true_for_known(self, storage_provider):
        self.add_test_app_user('existsAppUserTRUE', storage_provider)
        assert storage_provider.exists_app_username('existsAppUserTRUE')

    def test_exists_app_user_false_for_unknown(self, storage_provider):
        assert storage_provider.exists_app_username('existsAppUserUNKNOWN') is False

    def test_add_app_user_record_exists_after_commit(self, storage_provider):
        self.add_test_app_user('commitAppUserWORKS', storage_provider)
        storage_provider.commit()
        assert storage_provider.exists_app_username('commitAppUserWORKS')

    def test_add_app_user_record_gone_after_rollback(self, storage_provider):
        self.add_test_app_user('rollbackAppUserWORKS', storage_provider)
        storage_provider.rollback()
        assert not storage_provider.exists_app_username('rollbackAppUserWORKS')

    #endregion


    #region - test app_user methods

    def test_get_post_by_oid_unknown_raises(self, storage_provider):
        with pytest.raises(KeyError, match='post .oid=12345. does not exist'):
            storage_provider.get_post_by_oid('12345')

    def test_get_post_by_oid_gets_record(self, storage_provider):
        author = self.add_test_app_user('getPostByOIDGETS', storage_provider)
        original_post = self.add_test_post(author, storage_provider)
        stored_post = storage_provider.get_post_by_oid(original_post.oid)
        assert stored_post == original_post

    def add_test_post(self, author, storage_provider):
        title = author.name + "'s Post"
        body = 'My name is ' + author.name + '.'
        post = Post(title, body)
        post.author_oid = author.oid
        post.created_time = datetime.now(timezone.utc)
        post.oid = storage_provider.get_next_post_oid()
        storage_provider.add_post(post)
        return post

    def test_get_post_returns_a_copy(self, storage_provider):
        author = self.add_test_app_user('getPostRETURNS', storage_provider)
        original_post = self.add_test_post(author, storage_provider)
        copied_post = storage_provider.get_post_by_oid(original_post.oid)
        copied_post.title = 'Different'
        stored_post = storage_provider.get_post_by_oid(original_post.oid)
        assert stored_post != copied_post
        

    #endregion