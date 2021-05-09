import requests

from shrikenet.client.http_request_provider import HTTPRequestProvider
from shrikenet.client.http_response import HTTPResponse


class RequestsAdapter(HTTPRequestProvider):

    def __init__(self, base_url):
        self.base_url = base_url

    def get(self, url, json=None, token=None):
        return self.process_request('GET', url, json, token)

    def process_request(self, http_method, url, json=None, token=None):
        full_url = self.base_url + url
        headers = None if token is None else {'TOKEN': token}
        requests_response = requests.request(
            method=http_method,
            url=full_url,
            json=json,
            headers=headers,
        )
        return HTTPResponse(
            json=requests_response.json(),
            status_code=requests_response.status_code,
            status=requests_response.reason,
        )

    def post(self, url, json=None, token=None):
        return self.process_request('POST', url, json, token)

    def put(self, url, json=None, token=None):
        return self.process_request('PUT', url, json, token)

    def delete(self, url, json=None, token=None):
        return self.process_request('DELETE', url, json, token)
