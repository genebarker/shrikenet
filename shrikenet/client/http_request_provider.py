class HTTPRequestProvider:

    def __init__(self):
        raise NotImplementedError

    def get(self, url):
        raise NotImplementedError

    def post(self, url):
        raise NotImplementedError

    def put(self, url):
        raise NotImplementedError

    def delete(self, url):
        raise NotImplementedError
