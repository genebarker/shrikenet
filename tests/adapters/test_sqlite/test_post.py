from datetime import datetime, timedelta
from operator import attrgetter

import pytest

from shrikenet.adapters.sqlite import SQLite
from shrikenet.entities.app_user import AppUser
from shrikenet.entities.exceptions import (
    DatastoreKeyError,
)
from shrikenet.entities.post import Post, DeepPost

DATABASE = "test.db"


@pytest.fixture
def db():
    database = SQLite(DATABASE)
    database.open()
    database.build_database_schema()
    yield database
    database.close()


@pytest.fixture
def app_user(db):
    app_user = create_user()
    app_user.oid = db.add_app_user(app_user)
    return app_user


def create_user():
    oid = -1
    username = "mspacman"
    name = "Ms. Pacman"
    password_hash = "lowerUPPER"
    app_user = AppUser(
        oid,
        username,
        name,
        password_hash,
    )
    return app_user


@pytest.fixture
def post(app_user, db):
    return create_and_store_post(99, app_user, db)


def create_and_store_post(index, app_user, db):
    title = "Post Title #{}".format(index)
    body = "This is the body for post #{}.".format(index)
    time_now = datetime.now()
    my_post = Post(title, body)
    my_post.author_oid = app_user.oid
    my_post.created_time = time_now
    my_post.oid = db.add_post(my_post)
    return my_post


@pytest.fixture
def posts(app_user, db):
    my_posts = []
    for i in range(1, 6):
        my_posts.append(create_and_store_post(i, app_user, db))
    return my_posts


def test_get_post_by_oid_unknown_raises(db):
    regex = "can not get post .oid=12345., reason: "
    with pytest.raises(DatastoreKeyError, match=regex):
        db.get_post_by_oid("12345")


def test_get_post_by_oid_gets_record(post, db):
    stored_post = db.get_post_by_oid(post.oid)
    assert stored_post == post


def test_get_post_gets_deep_version(post, db):
    deep_post = db.get_post_by_oid(post.oid)
    assert deep_post.author_username == "mspacman"


def test_add_post_adds_record(post, db):
    stored_post = db.get_post_by_oid(post.oid)
    assert stored_post == post


def test_update_post_updates_record(post, db):
    post.title = "Different"
    db.update_post(post)
    stored_post = db.get_post_by_oid(post.oid)
    assert stored_post == post


def test_update_post_updates_every_field(post, db):
    user = AppUser(-1, "mrother", "Mr. Other", "fakeHASH")
    user.oid = db.add_app_user(user)
    post.title += "a"
    post.body += "b"
    post.author_oid = user.oid
    post.created_time = post.created_time - timedelta(hours=1)
    db.update_post(post)
    stored_post = db.get_post_by_oid(post.oid)
    assert stored_post == post


def test_update_post_raises_on_unknown_oid(db):
    unknown_post = Post("Some Title", "some content", oid=12345)
    regex = "can not update post .oid=12345., reason: "
    with pytest.raises(DatastoreKeyError, match=regex):
        db.update_post(unknown_post)


def test_delete_post_deletes(post, db):
    db.delete_post_by_oid(post.oid)
    with pytest.raises(DatastoreKeyError):
        db.get_post_by_oid(post.oid)


def test_add_post_record_exists_after_commit(post, db):
    db.commit()
    stored_post = db.get_post_by_oid(post.oid)
    assert stored_post == post


def test_add_post_record_gone_after_rollback(post, db):
    db.rollback()
    with pytest.raises(DatastoreKeyError):
        db.get_post_by_oid(post.oid)


def test_get_post_count_zero_when_empty(db):
    assert db.get_post_count() == 0


def test_get_post_count_matches_that_stored(posts, db):
    assert db.get_post_count() == len(posts)


def test_get_posts_matches_stored_and_LIFO_sorted(posts, db):
    stored_posts = db.get_posts()
    assert stored_posts == sorted(
        posts, key=attrgetter("created_time"), reverse=True
    )


def test_get_posts_gets_deep_versions(posts, db):
    stored_posts = db.get_posts()
    for post in stored_posts:
        assert isinstance(post, DeepPost)
        assert post.author_username == "mspacman"


def test_get_posts_returns_empty_list_when_empty(db):
    posts = db.get_posts()
    assert len(posts) == 0
