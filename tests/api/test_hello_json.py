import pytest


def test_naked_get_says_hello(client):
    response = client.get('/api/hello')
    json = response.get_json()
    assert json['error_code'] == 0
    assert json['message'] == 'Hello, World!'


@pytest.fixture
def token(client):
    response = client.post(
        '/api/get_token',
        json={
            'username': 'test',
            'password': 'test',
        },
    )
    json = response.get_json()
    return json['token']


def test_token_get_returns_expected(token, client):
    response = client.get(
        '/api/hello-get',
        headers={'TOKEN': token},
        json={'id1': 1, 'id2': 'two'},
    )
    verify_response_data(response, http_method='GET')


def verify_response_data(response, http_method):
    assert response.status_code == 200
    json = response.get_json()
    assert json['error_code'] == 0
    assert json['message'] == 'Hello, Mr. Test!'
    assert json['username'] == 'test'
    assert json['user_oid'] > 0
    assert json['http_method'] == http_method
    assert json['http_payload'] == {'id1': 1, 'id2': 'two'}


def test_token_post_returns_expected(token, client):
    response = client.post(
        '/api/hello-post',
        headers={'TOKEN': token},
        json={'id1': 1, 'id2': 'two'},
    )
    verify_response_data(response, http_method='POST')


def test_token_put_returns_expected(token, client):
    response = client.put(
        '/api/hello-put',
        headers={'TOKEN': token},
        json={'id1': 1, 'id2': 'two'},
    )
    verify_response_data(response, http_method='PUT')
