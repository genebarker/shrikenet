from shrikenet.client.http_response import HTTPResponse


def test_minimal_response_object(client):
    response = HTTPResponse(None)
    assert response.status_code == 200
    assert response.status == "200 OK"
