import pytest

from shrikenet.client.http_response import HTTPResponse
from shrikenet.client.flask_adapter import FlaskAdapter


class TestFlaskAdapter:

    @staticmethod
    def get_response_provider(client):
        return FlaskAdapter(client)

    @pytest.fixture
    def http(self, client):
        return self.get_response_provider(client)

    def test_get_hello_returns_response_object(self, http):
        response = http.get('/api/hello')
        assert isinstance(response, HTTPResponse)
        assert response.json == {
            'error_code': 0,
            'message': 'Hello, World!',
        }
        assert response.status_code == 200
        assert response.status.lower() == '200 ok'

    def test_bad_get_returns_expected_status(self, http):
        response = http.get('/NON/EXISTING/LINK')
        assert response.status_code == 404
        assert response.status.lower() == '404 not found'
