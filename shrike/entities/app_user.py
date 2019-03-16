from .validator import Validator


class AppUser:
    def __init__(self, username, name, password_hash):
        self.username = username
        self.name = name
        self.password_hash = password_hash
        self.validate_fields()

    def validate_fields(self):
        Validator.validate_username(self.username)
        Validator.validate_name(self.name)

    def __eq__(self, other):
        return (isinstance(other, AppUser) and
                self.username == other.username and
                self.name == other.name and
                self.password_hash == other.password_hash)
