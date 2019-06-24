from datetime import datetime, timezone

import pytest

from shrike.db import get_services


def test_index(client, auth):
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'test title' in response.data
    created_year = datetime(2018, 1, 1, tzinfo=timezone.utc).astimezone().date().year
    author_str = b'by test on Mon 01 Jan 2018' if created_year == 2018 \
        else b'by test on Sun 31 Dec 2017'
    assert author_str in response.data
    assert b'<p>test\nbody</p>' in response.data
    assert b'href="/1/update"' in response.data


@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers['Location'] == 'http://localhost/auth/login'


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
    assert client.post('/1/update').status_code == 403
    assert client.post('/1/delete').status_code == 403
    # current user doesn't see edit link
    assert b'href="/1/update"' not in client.get('/').data


@pytest.mark.parametrize('path', (
    '/2/update',
    '/2/delete',
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get('/create').status_code == 200
    client.post('/create', data={'title': 'created', 'body': ''})

    with app.app_context():
        storage_provider = get_services().storage_provider
        count = storage_provider.get_post_count()
        assert count == 2


def test_update(client, auth, app):
    auth.login()
    assert client.get('/1/update').status_code == 200
    client.post('/1/update', data={'title': 'updated', 'body': ''})

    with app.app_context():
        storage_provider = get_services().storage_provider
        post = storage_provider.get_post_by_oid(1)
        assert post.title == 'updated'


@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={'title': '', 'body': ''})
    assert b'Title is required.' in response.data


def test_delete(client, auth, app):
    auth.login()
    response = client.post('/1/delete')
    assert response.headers['Location'] == 'http://localhost/'

    with app.app_context():
        storage_provider = get_services().storage_provider
        with pytest.raises(KeyError):
            storage_provider.get_post_by_oid(1)
