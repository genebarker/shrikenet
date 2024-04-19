from datetime import datetime, timedelta, timezone
import json
import re

import httpretty
import pytest

from shrikenet import DEV_SECRET_KEY
from shrikenet.api.token_authority import create_token
from shrikenet.client.http_request_provider import HTTPRequestProvider
from shrikenet.client.http_response import HTTPResponse
from shrikenet.client.flask_adapter import FlaskAdapter
from shrikenet.client.requests_adapter import RequestsAdapter
from tests.api.test_token_authority import TEST_USER_OID


BASE_URL = "http://localhost:5000"


@pytest.fixture
def flask_http(client):
    yield FlaskAdapter(client)


@pytest.fixture
def requests_http():
    httpretty.enable()
    httpretty.register_uri(
        method=httpretty.GET,
        uri=f"{BASE_URL}/api/hello",
        body=json.dumps(
            {
                "error_code": 0,
                "message": "Hello, World!",
            }
        ),
    )
    register_uri_for_no_token_hellos()
    register_uri_for_unknown_links()
    yield RequestsAdapter(base_url=BASE_URL)
    httpretty.disable()
    httpretty.reset()


def register_uri_for_no_token_hellos():
    for http_method in ["GET", "POST", "PUT", "DELETE"]:
        method = getattr(httpretty, http_method)
        uri = f"{BASE_URL}/api/hello-{http_method.lower()}"
        httpretty.register_uri(
            method=method,
            uri=uri,
            body=json.dumps(
                {
                    "error_code": 1,
                    "message": "An authorization token is required.",
                }
            ),
        )


def register_uri_for_unknown_links():
    for http_method in ["GET", "POST", "PUT", "DELETE"]:
        method = getattr(httpretty, http_method)
        httpretty.register_uri(
            method=method,
            uri=re.compile(f"^{BASE_URL}/.*"),
            status=404,
        )


@pytest.fixture(params=["flask_http", "requests_http"])
def http(request):
    return request.getfixturevalue(request.param)


def test_is_a_http_request_provider(http):
    assert isinstance(http, HTTPRequestProvider)


def test_get_hello_returns_response_object(http):
    response = http.get("/api/hello")
    assert isinstance(response, HTTPResponse)
    assert response.json == {
        "error_code": 0,
        "message": "Hello, World!",
    }
    assert response.status_code == 200
    assert response.status.lower().endswith("ok")


@pytest.mark.parametrize("http_method", ["get", "post", "put", "delete"])
def test_bad_links_return_expected_status(http, http_method):
    http_call = getattr(http, http_method)  # i.e. http.get()
    response = http_call("/NON/EXISTING/LINK")
    assert response.status_code == 404
    assert response.status.lower().endswith("not found")


@pytest.mark.parametrize("http_method", ["get", "post", "put", "delete"])
def test_unauthorized_http_method_returns_expected(http, http_method):
    http_call = getattr(http, http_method)  # i.e. http.get()
    response = http_call(f"/api/hello-{http_method}")
    assert response.status_code == 200
    assert response.status.lower().endswith("ok")
    assert response.json == {
        "error_code": 1,
        "message": "An authorization token is required.",
    }


@pytest.mark.parametrize("http_method", ["get", "post", "put", "delete"])
def test_authorized_http_method_returns_expected(http, http_method):
    http_call = getattr(http, http_method)  # i.e. http.get()
    token = get_auth_token()
    response = http_call(
        url=f"/api/hello-{http_method}",
        token=token,
    )
    assert response.status_code == 200


def get_auth_token():
    user_oid = TEST_USER_OID
    expire_time = datetime.now(timezone.utc) + timedelta(days=1)
    secret_key = DEV_SECRET_KEY
    return create_token(user_oid, expire_time, secret_key)
