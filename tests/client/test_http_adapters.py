import json
import re

import httpretty
import pytest

from shrikenet.client.http_request_provider import HTTPRequestProvider
from shrikenet.client.http_response import HTTPResponse
from shrikenet.client.flask_adapter import FlaskAdapter
from shrikenet.client.requests_adapter import RequestsAdapter


BASE_URL = 'http://localhost:5000'


@pytest.fixture
def flask_http(client):
    yield FlaskAdapter(client)


@pytest.fixture
def requests_http():
    httpretty.enable()
    httpretty.register_uri(
        method=httpretty.GET,
        uri=f'{BASE_URL}/api/hello',
        body=json.dumps({
            'error_code': 0,
            'message': 'Hello, World!',
        }),
    )
    httpretty.register_uri(
        method=httpretty.GET,
        uri=re.compile(f'^{BASE_URL}/.*'),
        status=404,
    )
    yield RequestsAdapter(base_url=BASE_URL)
    httpretty.disable()
    httpretty.reset()


@pytest.fixture(params=['flask_http', 'requests_http'])
def http(request):
    return request.getfixturevalue(request.param)


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
