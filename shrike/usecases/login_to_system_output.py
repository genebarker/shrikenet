class LoginToSystemOutput:

    def __init__(self, login_successful=False, message='Login attempt failed.'):
        self.login_successful = login_successful
        self.message = message
