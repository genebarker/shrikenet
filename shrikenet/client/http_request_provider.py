class HTTPRequestProvider:

    def __init__(self):
        raise NotImplementedError

    def get(self, url, json=None, token=None):
        raise NotImplementedError

    def post(self, url, json=None, token=None):
        raise NotImplementedError

    def put(self, url, json=None, token=None):
        raise NotImplementedError

    def delete(self, url, json=None, token=None):
        raise NotImplementedError
