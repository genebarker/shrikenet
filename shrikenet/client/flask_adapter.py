from shrikenet.client.http_request_provider import HTTPRequestProvider
from shrikenet.client.http_response import HTTPResponse


class FlaskAdapter(HTTPRequestProvider):

    def __init__(self, test_client):
        self.client = test_client

    def get(self, url, json=None, token=None):
        return self.process_request("GET", url, json, token)

    def process_request(self, http_method, url, json=None, token=None):
        http_call = getattr(self.client, http_method.lower())
        headers = None if token is None else {"TOKEN": token}
        response = http_call(url, json=json, headers=headers)
        json_out = response.get_json() if response.is_json else None
        return HTTPResponse(
            json=json_out,
            status_code=response.status_code,
            status=response.status,
        )

    def post(self, url, json=None, token=None):
        return self.process_request("POST", url, json, token)

    def put(self, url, json=None, token=None):
        return self.process_request("PUT", url, json, token)

    def delete(self, url, json=None, token=None):
        return self.process_request("DELETE", url, json, token)
