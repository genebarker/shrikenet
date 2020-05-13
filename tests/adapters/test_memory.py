import copy
from datetime import datetime, timedelta, timezone
from operator import attrgetter

import pytest

from shrikenet.adapters.memory import Memory
from shrikenet.entities.app_user import AppUser
from shrikenet.entities.exceptions import (
    DatastoreClosed,
    DatastoreAlreadyOpen,
    DatastoreError,
    DatastoreKeyError,
)
from shrikenet.entities.post import DeepPost, Post
from shrikenet.entities.rules import Rules
from shrikenet.entities.storage_provider import StorageProvider


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

    # region - test general properties

    def test_is_a_storage_provider(self, storage_provider):
        assert isinstance(storage_provider, StorageProvider)

    def test_get_version_returns_provider_info(self, storage_provider):
        assert storage_provider.get_version().startswith(
            storage_provider.VERSION_PREFIX)

    def test_raises_when_not_opened_first(self):
        storage_provider = self.get_storage_provider()
        with pytest.raises(DatastoreClosed) as excinfo:
            storage_provider.get_version()
        assert str(excinfo.value) == (
            'get_version is not available since the connection is closed'
        )

    def test_raises_when_already_opened(self, storage_provider):
        with pytest.raises(DatastoreAlreadyOpen) as excinfo:
            storage_provider.open()
        assert str(excinfo.value) == 'connection already open'

    def test_raises_when_already_closed(self):
        storage_provider = self.get_storage_provider()
        storage_provider.open()
        storage_provider.close()
        with pytest.raises(DatastoreClosed):
            storage_provider.get_version()

    # endregion

    # region - test transaction handling

    def test_commit_can_be_called_after_no_action(self, storage_provider):
        storage_provider.commit()
        storage_provider.commit()

    def test_rollback_can_be_called_after_no_action(self, storage_provider):
        storage_provider.rollback()
        storage_provider.rollback()

    # endregion

    # region - test schema build / reset methods

    def test_schema_exists_after_build(self, storage_provider):
        storage_provider.build_database_schema()
        self.assert_database_in_initial_state(storage_provider)

    def assert_database_in_initial_state(self, storage_provider):
        assert storage_provider.get_app_user_count() == 0
        assert storage_provider.get_post_count() == 0
        assert storage_provider.get_next_app_user_oid() == 1
        assert storage_provider.get_next_post_oid() == 1

    def test_database_objects_reset_to_initial_state(self, storage_provider):
        storage_provider.reset_database_objects()
        self.assert_database_in_initial_state(storage_provider)

    # endregion

    # region - test get next ID methods

    GET_NEXT_OID_METHODS = ['get_next_app_user_oid', 'get_next_post_oid']

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

    # endregion

    # region - test app_user methods

    GOOD_USERNAME = 'mawesome'

    @pytest.fixture
    def app_user(self, storage_provider):
        oid = storage_provider.get_next_app_user_oid()
        username = self.GOOD_USERNAME
        name = 'Mr. Awesome'
        password_hash = 'xxYYYzzzz'
        time_now = datetime.now(timezone.utc)
        app_user = AppUser(oid, username, name, password_hash,
                           needs_password_change=True,
                           is_locked=True,
                           is_dormant=True,
                           ongoing_password_failure_count=2,
                           last_password_failure_time=time_now)
        storage_provider.add_app_user(app_user)
        return app_user

    def test_get_app_user_by_username_unknown_raises(self, storage_provider):
        regex = 'can not get app_user .username=xyz., reason: '
        with pytest.raises(DatastoreKeyError, match=regex):
            storage_provider.get_app_user_by_username('xyz')

    def test_get_app_user_by_username_gets_record(self, app_user,
                                                  storage_provider):
        original_user = app_user
        stored_user = storage_provider.get_app_user_by_username(
            original_user.username)
        assert stored_user == original_user

    def test_get_app_user_by_oid_unknown_raises(self, storage_provider):
        regex = 'can not get app_user .oid=12345., reason: '
        with pytest.raises(DatastoreKeyError, match=regex):
            storage_provider.get_app_user_by_oid('12345')

    def test_get_app_user_by_oid_gets_record(self, app_user,
                                             storage_provider):
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

    def test_add_app_user_with_duplicate_username_raises(self, app_user,
                                                         storage_provider):
        new_user = copy.copy(app_user)
        new_user.oid = 100
        regex = ('can not add app_user .oid={}, username={}., reason: '
                 .format(new_user.oid, app_user.username))
        with pytest.raises(DatastoreError, match=regex):
            storage_provider.add_app_user(new_user)

    def test_add_app_user_with_duplicate_oid_raises(self, app_user,
                                                    storage_provider):
        new_user = copy.copy(app_user)
        new_user.username = 'Different'
        regex = ('can not add app_user .oid={}, username={}., reason: '
                 .format(app_user.oid, new_user.username))
        with pytest.raises(DatastoreError, match=regex):
            storage_provider.add_app_user(new_user)

    def test_update_app_user_updates_record(self, app_user,
                                            storage_provider):
        app_user.name = 'Different'
        storage_provider.update_app_user(app_user)
        stored_user = storage_provider.get_app_user_by_oid(app_user.oid)
        assert stored_user == app_user

    def test_update_app_user_updates_a_copy(self, app_user,
                                            storage_provider):
        app_user.name = 'Different'
        storage_provider.update_app_user(app_user)
        app_user.name = 'Very Different'
        stored_user = storage_provider.get_app_user_by_oid(app_user.oid)
        assert stored_user != app_user

    def test_update_app_user_updates_every_field(self, app_user,
                                                 storage_provider):
        app_user.username += 'a'
        app_user.name += 'b'
        app_user.password_hash += 'c'
        app_user.needs_password_change = not app_user.needs_password_change
        app_user.is_locked = not app_user.is_locked
        app_user.is_dormant = not app_user.is_dormant
        app_user.ongoing_password_failure_count += 1
        app_user.last_password_failure_time = (
            app_user.last_password_failure_time - timedelta(hours=1))
        storage_provider.update_app_user(app_user)
        stored_user = storage_provider.get_app_user_by_oid(app_user.oid)
        assert stored_user == app_user

    def test_get_app_user_count_zero_when_empty(self, storage_provider):
        assert storage_provider.get_app_user_count() == 0

    def test_get_app_user_count_matches_that_stored(self, app_user,
                                                    storage_provider):
        assert storage_provider.get_app_user_count() == 1

    def test_exists_app_user_true_for_known(self, app_user,
                                            storage_provider):
        assert storage_provider.exists_app_username(app_user.username)

    def test_exists_app_user_false_for_unknown(self, storage_provider):
        assert storage_provider.exists_app_username('UNKNOWN') is False

    def test_add_app_user_record_exists_after_commit(self, app_user,
                                                     storage_provider):
        storage_provider.commit()
        assert storage_provider.exists_app_username(app_user.username)

    def test_add_app_user_record_gone_after_rollback(self, app_user,
                                                     storage_provider):
        storage_provider.rollback()
        assert not storage_provider.exists_app_username(app_user.username)

    # endregion

    # region - test post methods

    @pytest.fixture
    def post(self, app_user, storage_provider):
        return self.create_and_store_post(99, app_user, storage_provider)

    def create_and_store_post(self, index, app_user, storage_provider):
        title = 'Post Title #{}'.format(index)
        body = 'This is the body for post #{}.'.format(index)
        post = Post(title, body)
        post.author_oid = app_user.oid
        post.created_time = datetime.now(timezone.utc)
        post.oid = storage_provider.get_next_post_oid()
        storage_provider.add_post(post)
        return post

    @pytest.fixture
    def posts(self, app_user, storage_provider):
        posts = []
        for i in range(1, 6):
            posts.append(self.create_and_store_post(i, app_user,
                                                    storage_provider))
        return posts

    def test_get_post_by_oid_unknown_raises(self, storage_provider):
        regex = 'can not get post .oid=12345., reason: '
        with pytest.raises(DatastoreKeyError, match=regex):
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

    def test_add_post_with_duplicate_oid_raises(self, post,
                                                storage_provider):
        new_post = copy.copy(post)
        regex = ('can not add post .oid={}, title={}., reason: '
                 .format(new_post.oid, new_post.title))
        with pytest.raises(DatastoreError, match=regex):
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

    def test_delete_post_deletes(self, post, storage_provider):
        storage_provider.delete_post_by_oid(post.oid)
        with pytest.raises(DatastoreKeyError):
            storage_provider.get_post_by_oid(post.oid)

    def test_add_post_record_exists_after_commit(self, post,
                                                 storage_provider):
        storage_provider.commit()
        stored_post = storage_provider.get_post_by_oid(post.oid)
        assert stored_post == post

    def test_add_post_record_gone_after_rollback(self, post,
                                                 storage_provider):
        storage_provider.rollback()
        with pytest.raises(DatastoreKeyError):
            storage_provider.get_post_by_oid(post.oid)

    def test_get_post_count_zero_when_empty(self, storage_provider):
        assert storage_provider.get_post_count() == 0

    def test_get_post_count_matches_that_stored(self, posts,
                                                storage_provider):
        assert storage_provider.get_post_count() == len(posts)

    def test_get_posts_matches_stored_and_LIFO_sorted(self, posts,
                                                      storage_provider):
        stored_posts = storage_provider.get_posts()
        assert stored_posts == sorted(posts, key=attrgetter('created_time'),
                                      reverse=True)

    def test_get_posts_gets_deep_versions(self, posts, storage_provider):
        stored_posts = storage_provider.get_posts()
        for post in stored_posts:
            assert isinstance(post, DeepPost)
            assert post.author_username == self.GOOD_USERNAME

    def test_get_posts_returns_empty_list_when_empty(self, storage_provider):
        posts = storage_provider.get_posts()
        assert len(posts) == 0

    # endregion

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
