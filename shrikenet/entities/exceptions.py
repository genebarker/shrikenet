class ShrikeException(Exception):

    def __init__(self, message=None):
        if message is None:
            message = "an unexpected error occurred"
        super().__init__(message)


class DatastoreClosed(ShrikeException):
    pass


class DatastoreAlreadyOpen(ShrikeException):
    pass


class DatastoreError(ShrikeException):
    pass


class DatastoreKeyError(ShrikeException, KeyError):
    pass
