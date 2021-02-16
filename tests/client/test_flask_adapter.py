from shrikenet.client.http_response import HTTPResponse
from shrikenet.client.flask_adapter import FlaskAdapter


def test_get_hello_returns_response_object(client):
    http = FlaskAdapter(client)
    response = http.get('/api/hello')
    assert isinstance(response, HTTPResponse)
    assert response.json == {
        'error_code': 0,
        'message': 'Hello, World!',
    }
    assert response.status_code == 200
    assert response.status.lower() == '200 ok'


def test_bad_get_returns_expected_status(client):
    http = FlaskAdapter(client)
    response = http.get('/NON/EXISTING/LINK')
    assert response.status_code == 404
    assert response.status.lower() == '404 not found'
