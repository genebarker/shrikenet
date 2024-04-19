class Rules:

    DEFAULT_LOGIN_FAIL_THRESHOLD_COUNT = 3
    DEFAULT_LOGIN_FAIL_LOCK_MINUTES = 15

    def __init__(self):
        self.login_fail_threshold_count = (
            self.DEFAULT_LOGIN_FAIL_THRESHOLD_COUNT
        )
        self.login_fail_lock_minutes = self.DEFAULT_LOGIN_FAIL_LOCK_MINUTES

    def __eq__(self, other):
        return (
            isinstance(other, Rules)
            and self.login_fail_threshold_count
            == other.login_fail_threshold_count
            and self.login_fail_lock_minutes
            == other.login_fail_lock_minutes
        )
