class LoginToSystemResult:

    def __init__(self, message, was_successful=False,
                 must_change_password=False):
        self.message = message
        self.was_successful = was_successful
        self.must_change_password = must_change_password
