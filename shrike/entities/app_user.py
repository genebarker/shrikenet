class AppUser:

    def __init__(self, oid, username, name, password_hash,
                 needs_password_change=False):
        self.oid = oid
        self.username = username
        self.name = name
        self.password_hash = password_hash
        self.needs_password_change = needs_password_change

    def __eq__(self, other):
        return (isinstance(other, AppUser) and
                self.oid == other.oid and
                self.username == other.username and
                self.name == other.name and
                self.password_hash == other.password_hash and
                self.needs_password_change == other.needs_password_change)
