from datetime import datetime, timezone

import pytest

from shrikenet.db import get_services


def test_index(client, auth):
    response = client.get("/")
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get("/")
    assert b"Log Out" in response.data
    assert b"test title" in response.data

    created_time_utc = datetime(2018, 1, 1, tzinfo=timezone.utc)
    created_time_local = created_time_utc.astimezone()
    created_year_local = created_time_local.date().year
    author_str = (
        b"by test on Mon 01 Jan 2018"
        if created_year_local == 2018
        else b"by test on Sun 31 Dec 2017"
    )
    assert author_str in response.data
    assert b"<p>test body</p>" in response.data
    assert b'href="/1/update"' in response.data


def get_year_in_local_time_zone(dt):
    return dt.astimezone().date().year


@pytest.mark.parametrize(
    "path",
    (
        "/create",
        "/1/update",
        "/1/delete",
    ),
)
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login"


def test_author_required(app, client, auth):
    # change the post author to another user
    with app.app_context():
        storage_provider = get_services().storage_provider
        post = storage_provider.get_post_by_oid(1)
        post.author_oid = 2
        storage_provider.update_post(post)
        storage_provider.commit()

    auth.login()
    # current user can't modify other user's post
    assert client.post("/1/update").status_code == 403
    assert client.post("/1/delete").status_code == 403
    # current user doesn't see edit link
    assert b'href="/1/update"' not in client.get("/").data


@pytest.mark.parametrize(
    "path",
    (
        "/2/update",
        "/2/delete",
    ),
)
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get("/create").status_code == 200
    client.post("/create", data={"title": "created", "body": ""})

    with app.app_context():
        storage_provider = get_services().storage_provider
        count = storage_provider.get_post_count()
        assert count == 2


def test_update(client, auth, app):
    auth.login()
    assert client.get("/1/update").status_code == 200
    client.post("/1/update", data={"title": "updated", "body": ""})

    with app.app_context():
        storage_provider = get_services().storage_provider
        post = storage_provider.get_post_by_oid(1)
        assert post.title == "updated"


@pytest.mark.parametrize(
    "path",
    (
        "/create",
        "/1/update",
    ),
)
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={"title": "", "body": ""})
    assert b"Title is required." in response.data


def test_delete(client, auth, app):
    auth.login()
    response = client.post("/1/delete")
    assert response.headers["Location"] == "/"

    with app.app_context():
        storage_provider = get_services().storage_provider
        with pytest.raises(KeyError):
            storage_provider.get_post_by_oid(1)
