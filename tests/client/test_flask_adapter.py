from shrikenet.client.flask_adapter import FlaskAdapter


def test_get_hello(client):
    http = FlaskAdapter(client)
    response = http.get('/hello')
    assert b'Hello, World!' in response.data
