import pytest

from shrikenet.client.http_request_provider import HTTPRequestProvider


class TestHTTPRequestProvider:

    def test_interface_cant_be_instantiated(self):
        with pytest.raises(NotImplementedError):
            HTTPRequestProvider()

    @pytest.fixture
    def http(self):
        class FakeAdapter(HTTPRequestProvider):
            def __init__(self):
                pass
        return FakeAdapter()


    @pytest.mark.parametrize('http_method', ['get', 'post', 'put', 'delete'])
    def test_get_cant_be_called(self, http, http_method):
        http_call = getattr(http, http_method)  # i.e. http.get()
        with pytest.raises(NotImplementedError):
            http_call('http://example.com')
