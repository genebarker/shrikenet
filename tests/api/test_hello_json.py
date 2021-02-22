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
    response = client.get('/api/hello-get', headers={'TOKEN': token})
    assert response.status_code == 200
    json = response.get_json()
    assert json['error_code'] == 0
    assert json['username'] == 'test'
    assert json['user_oid'] > 0
    assert json['http_method'] == 'GET'
