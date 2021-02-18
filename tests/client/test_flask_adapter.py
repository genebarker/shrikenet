import pytest

from shrikenet.client.http_request_provider import HTTPRequestProvider
from shrikenet.client.http_response import HTTPResponse
from shrikenet.client.flask_adapter import FlaskAdapter


@pytest.fixture
def http(client):
    yield FlaskAdapter(client)


def test_is_a_http_request_provider(http):
    assert isinstance(http, HTTPRequestProvider)


def test_get_hello_returns_response_object(http):
    response = http.get('/api/hello')
    assert isinstance(response, HTTPResponse)
    assert response.json == {
        'error_code': 0,
        'message': 'Hello, World!',
    }
    assert response.status_code == 200
    assert response.status.lower().endswith('ok')


def test_bad_get_returns_expected_status(http):
    response = http.get('/NON/EXISTING/LINK')
    assert response.status_code == 404
    assert response.status.lower().endswith('not found')
