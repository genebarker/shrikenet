class AppUser:

    def __init__(self, oid, username, name, password_hash,
                 needs_password_change=False, is_locked=False,
                 is_dormant=False, ongoing_login_failure_count=0,
                 last_login_failure_time=None):
        self.oid = oid
        self.username = username
        self.name = name
        self.password_hash = password_hash
        self.needs_password_change = needs_password_change
        self.is_locked = is_locked
        self.is_dormant = is_dormant
        self.ongoing_login_failure_count = ongoing_login_failure_count
        self.last_login_failure_time = last_login_failure_time

    def __eq__(self, other):
        return (isinstance(other, AppUser) and
                self.oid == other.oid and
                self.username == other.username and
                self.name == other.name and
                self.password_hash == other.password_hash and
                self.needs_password_change == other.needs_password_change and
                self.is_locked == other.is_locked and
                self.is_dormant == other.is_dormant and
                self.ongoing_login_failure_count ==
                other.ongoing_login_failure_count and
                self.last_login_failure_time == other.last_login_failure_time)
