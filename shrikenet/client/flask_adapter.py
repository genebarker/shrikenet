from shrikenet.client.http_request_provider import HTTPRequestProvider
from shrikenet.client.http_response import HTTPResponse


class FlaskAdapter(HTTPRequestProvider):

    def __init__(self, test_client):
        self.client = test_client

    def get(self, url):
        return self.process_request('GET', url)

    def process_request(self, http_method, url):
        http_call = getattr(self.client, http_method.lower())
        flask_response = http_call(url)
        json = flask_response.get_json() if flask_response.is_json else None
        return HTTPResponse(
            json=json,
            status_code=flask_response.status_code,
            status=flask_response.status,
        )

    def post(self, url):
        return self.process_request('POST', url)

    def put(self, url):
        return self.process_request('PUT', url)

    def delete(self, url):
        return self.process_request('DELETE', url)
