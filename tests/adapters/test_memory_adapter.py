import copy
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

    @pytest.fixture
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
        with pytest.raises(Exception):
            storage_provider.get_version()

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

    GOOD_USERNAME = 'mawesome'

    @pytest.fixture
    def app_user(self, storage_provider):
        oid = storage_provider.get_next_app_user_oid()
        username = self.GOOD_USERNAME
        name = 'Mr. Awesome'
        password_hash = 'xxYYYzzzz'
        app_user = AppUser(oid, username, name, password_hash)
        storage_provider.add_app_user(app_user)
        return app_user

    def test_get_app_user_by_username_unknown_raises(self, storage_provider):
        with pytest.raises(Exception, match='can not get app_user .username=xyz., reason: '):
            storage_provider.get_app_user_by_username('xyz')

    def test_get_app_user_by_username_gets_record(self, app_user, storage_provider):
        original_user = app_user
        stored_user = storage_provider.get_app_user_by_username(original_user.username)
        assert stored_user == original_user

    def test_get_app_user_by_oid_unknown_raises(self, storage_provider):
        with pytest.raises(Exception, match='can not get app_user .oid=12345., reason: '):
            storage_provider.get_app_user_by_oid('12345')

    def test_get_app_user_by_oid_gets_record(self, app_user, storage_provider):
        stored_user = storage_provider.get_app_user_by_oid(app_user.oid)
        assert stored_user == app_user

    def test_get_app_user_returns_a_copy(self, app_user, storage_provider):
        copied_user = storage_provider.get_app_user_by_oid(app_user.oid)
        copied_user.name = 'Different'
        stored_user = storage_provider.get_app_user_by_oid(app_user.oid)
        assert stored_user != copied_user

    def test_add_app_user_adds_record(self, app_user, storage_provider):
        stored_user = storage_provider.get_app_user_by_oid(app_user.oid)
        assert stored_user == app_user

    def test_add_app_user_adds_a_copy(self, app_user, storage_provider):
        app_user.name = 'Different'
        stored_user = storage_provider.get_app_user_by_oid(app_user.oid)
        assert stored_user != app_user

    def test_add_app_user_with_duplicate_username_raises(self, app_user, storage_provider):
        new_user = copy.copy(app_user)
        new_user.oid = 100
        with pytest.raises(Exception, match='can not add app_user .oid={}, username={}., reason: '.format(new_user.oid, app_user.username)):
            storage_provider.add_app_user(new_user)

    def test_add_app_user_with_duplicate_oid_raises(self, app_user, storage_provider):
        new_user = copy.copy(app_user)
        new_user.username = 'Different'
        with pytest.raises(Exception, match='can not add app_user .oid={}, username={}., reason: '.format(app_user.oid, new_user.username)):
            storage_provider.add_app_user(new_user)

    def test_update_app_user_updates_record(self, app_user, storage_provider):
        app_user.name = 'Different'
        storage_provider.update_app_user(app_user)
        stored_user = storage_provider.get_app_user_by_oid(app_user.oid)
        assert stored_user == app_user

    def test_update_app_user_updates_a_copy(self, app_user, storage_provider):
        app_user.name = 'Different'
        storage_provider.update_app_user(app_user)
        app_user.name = 'Very Different'
        stored_user = storage_provider.get_app_user_by_oid(app_user.oid)
        assert stored_user != app_user

    def test_exists_app_user_true_for_known(self, app_user, storage_provider):
        assert storage_provider.exists_app_username(app_user.username)

    def test_exists_app_user_false_for_unknown(self, storage_provider):
        assert storage_provider.exists_app_username('UNKNOWN') is False

    def test_add_app_user_record_exists_after_commit(self, app_user, storage_provider):
        storage_provider.commit()
        assert storage_provider.exists_app_username(app_user.username)

    def test_add_app_user_record_gone_after_rollback(self, app_user, storage_provider):
        storage_provider.rollback()
        assert not storage_provider.exists_app_username(app_user.username)

    #endregion


    #region - test post methods

    @pytest.fixture
    def post(self, app_user, storage_provider):
        title = 'Post Title'
        body = 'This is the body.'
        post = Post(title, body)
        post.author_oid = app_user.oid
        post.created_time = datetime.now(timezone.utc)
        post.oid = storage_provider.get_next_post_oid()
        storage_provider.add_post(post)
        return post

    def test_get_post_by_oid_unknown_raises(self, storage_provider):
        with pytest.raises(Exception, match='can not get post .oid=12345., reason: '):
            storage_provider.get_post_by_oid('12345')

    def test_get_post_by_oid_gets_record(self, post, storage_provider):
        stored_post = storage_provider.get_post_by_oid(post.oid)
        assert stored_post == post

    def test_get_post_gets_deep_version(self, post, storage_provider):
        deep_post = storage_provider.get_post_by_oid(post.oid)
        assert deep_post.author_username == self.GOOD_USERNAME

    def test_get_post_returns_a_copy(self, post, storage_provider):
        copied_post = storage_provider.get_post_by_oid(post.oid)
        copied_post.title = 'Different'
        stored_post = storage_provider.get_post_by_oid(post.oid)
        assert stored_post != copied_post
        
    def test_add_post_adds_record(self, post, storage_provider):
        stored_post = storage_provider.get_post_by_oid(post.oid)
        assert stored_post == post

    def test_add_post_adds_a_copy(self, post, storage_provider):
        post.title = 'Different'
        stored_post = storage_provider.get_post_by_oid(post.oid)
        assert stored_post != post

    def test_add_post_with_duplicate_oid_raises(self, post, storage_provider):
        new_post = copy.copy(post)
        with pytest.raises(Exception, match='can not add post .oid={}, title={}., reason: '.format(new_post.oid, new_post.title)):
            storage_provider.add_post(new_post)

    def test_update_post_updates_record(self, post, storage_provider):
        post.title = 'Different'
        storage_provider.update_post(post)
        stored_post = storage_provider.get_post_by_oid(post.oid)
        assert stored_post == post

    def test_update_post_updates_a_copy(self, post, storage_provider):
        post.title = 'Different'
        storage_provider.update_post(post)
        post.title = 'Very Different'
        stored_post = storage_provider.get_post_by_oid(post.oid)
        assert stored_post != post

    def test_add_post_record_exists_after_commit(self, post, storage_provider):
        storage_provider.commit()
        stored_post = storage_provider.get_post_by_oid(post.oid)
        assert stored_post == post

    def test_add_post_record_gone_after_rollback(self, post, storage_provider):
        storage_provider.rollback()
        with pytest.raises(KeyError):
            storage_provider.get_post_by_oid(post.oid)

    #endregion
