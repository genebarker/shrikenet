class Post:

    def __init__(self, title, body, oid=None, author_oid=None, created_time=None):
        self.oid = oid
        self.title = title
        self.body = body
        self.author_oid = author_oid
        self.created_time = created_time

    def __eq__(self, other):
        return (isinstance(other, Post) and
                self.oid == other.oid and
                self.title == other.title and
                self.body == other.body and
                self.author_oid == other.author_oid and
                self.created_time == other.created_time)
