import requests

from shrikenet.client.http_request_provider import HTTPRequestProvider
from shrikenet.client.http_response import HTTPResponse


class RequestsAdapter(HTTPRequestProvider):

    def __init__(self, base_url):
        self.base_url = base_url

    def get(self, url):
        return self.process_request('GET', url)

    def process_request(self, http_method, url):
        full_url = self.base_url + url
        requests_response = requests.request(
            method=http_method,
            url=full_url,
        )
        return HTTPResponse(
            json=requests_response.json(),
            status_code=requests_response.status_code,
            status=requests_response.reason,
        )

    def post(self, url):
        return self.process_request('POST', url)

    def put(self, url):
        return self.process_request('PUT', url)

    def delete(self, url):
        return self.process_request('DELETE', url)
