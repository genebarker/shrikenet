class Post:

    def __init__(self, title, body, oid=None, author_oid=None, created_time=None):
        self.oid = oid
        self.author_oid = author_oid
        self.created_time = created_time
        self.title = title
        self.body = body
