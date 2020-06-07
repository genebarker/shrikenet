import copy
from datetime import datetime, timezone
from operator import attrgetter

import pytest

from shrikenet.adapters.memory import Memory
from shrikenet.entities.app_user import AppUser
from shrikenet.entities.exceptions import (
    DatastoreError,
    DatastoreKeyError,
)
from shrikenet.entities.post import DeepPost, Post
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
