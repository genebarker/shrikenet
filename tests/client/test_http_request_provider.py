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

    def test_get_cant_be_called(self, http):
        with pytest.raises(NotImplementedError):
            http.get('http://example.com')
