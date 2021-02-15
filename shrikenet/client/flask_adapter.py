class FlaskAdapter:

    def __init__(self, test_client):
        self.client = test_client

    def get(self, url):
        return self.client.get(url)
