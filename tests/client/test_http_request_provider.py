import json
import pytest

from shrikenet.client.http_request_provider import HTTPRequestProvider


def test_interface_cant_be_instantiated():
    with pytest.raises(NotImplementedError):
        HTTPRequestProvider()


@pytest.fixture
def http():
    class FakeAdapter(HTTPRequestProvider):
        def __init__(self):
            pass
    return FakeAdapter()


@pytest.mark.parametrize('http_method', ['get', 'post', 'put', 'delete'])
def test_methods_cant_be_called(http, http_method):
    http_call = getattr(http, http_method)  # i.e. http.get()
    with pytest.raises(NotImplementedError):
        http_call('http://example.com')


@pytest.mark.parametrize('http_method', ['get', 'post', 'put', 'delete'])
def test_methods_accept_parms(http, http_method):
    http_call = getattr(http, http_method)  # i.e. http.get()
    json_data = json.dumps({})
    with pytest.raises(NotImplementedError):
        http_call('http://example.com', json=json_data)
    with pytest.raises(NotImplementedError):
        http_call('http://example.com', json=json_data, token='tOkEn_data')
