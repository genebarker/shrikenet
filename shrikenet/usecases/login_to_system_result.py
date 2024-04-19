class LoginToSystemResult:

    def __init__(
        self,
        message,
        has_failed=True,
        must_change_password=False,
        user_oid=None,
    ):
        self.message = message
        self.has_failed = has_failed
        self.must_change_password = must_change_password
        self.user_oid = user_oid
