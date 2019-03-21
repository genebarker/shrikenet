from .validator import Validator


class AppUser:
    def __init__(self, username, name, password_hash):
        self.id = None
        self.username = username
        self.name = name
        self.password_hash = password_hash

    def __eq__(self, other):
        return (isinstance(other, AppUser) and
                self.id == other.id and
                self.username == other.username and
                self.name == other.name and
                self.password_hash == other.password_hash)
