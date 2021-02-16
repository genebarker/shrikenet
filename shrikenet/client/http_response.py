class HTTPResponse:

    def __init__(self, json, status_code=200, status='OK'):
        self.json = json
        self.status_code = status_code
        self.status = status
