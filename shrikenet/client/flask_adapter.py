from shrikenet.client.http_response import HTTPResponse


class FlaskAdapter:

    def __init__(self, test_client):
        self.client = test_client

    def get(self, url):
        flask_response = self.client.get(url)
        json = flask_response.get_json() if flask_response.is_json else None
        return HTTPResponse(
            json=json,
            status_code=flask_response.status_code,
            status=flask_response.status,
        )
