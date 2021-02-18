import requests

from shrikenet.client.http_request_provider import HTTPRequestProvider
from shrikenet.client.http_response import HTTPResponse


class RequestsAdapter(HTTPRequestProvider):

    def __init__(self, base_url):
        self.base_url = base_url

    def get(self, url):
        full_url = self.base_url + url
        requests_response = requests.get(full_url)
        print('I got here!')
        return HTTPResponse(
            json=requests_response.json(),
            status_code=requests_response.status_code,
            status=requests_response.reason,
        )
