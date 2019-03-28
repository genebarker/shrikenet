import copy

from shrike.entities.storage_provider import StorageProvider


class MemoryAdapter(StorageProvider):

    VERSION_PREFIX = "MemoryStore"
    VERSION_NUMBER = "1.0"

    def __init__(self):
        self.app_user = {}
        self.app_user_next_id = 1
        self.is_open = False

    def save_tables(self):
        self.saved_app_user = {}
        for key, value in self.app_user.items():
            self.saved_app_user[key] = copy.copy(value)

    def restore_tables(self):
        self.app_user = {}
        for key, value in self.saved_app_user.items():
            self.app_user[key] = copy.copy(value)


    # restrict access to attributes when closed
    def __getattribute__(self, name):
        if (name not in ('open', 'is_open') and not self.is_open):
            error = '{0} is not available since the connection is closed'.format(name)
            raise Exception(error)
        return object.__getattribute__(self, name)

    def open(self):
        if self.is_open:
            raise Exception('connection already open')
        self.is_open = True
        self.save_tables()

    def close(self):
        self.restore_tables()
        self.is_open = False

    def commit(self):
        self.save_tables()

    def rollback(self):
        self.restore_tables()

    def get_version(self):
        return ("{0} {1} - a lightweight in-memory database for unit testing"
                .format(self.VERSION_PREFIX, self.VERSION_NUMBER))
        
    def get_next_app_user_id(self):
        next_id = self.app_user_next_id
        self.app_user_next_id += 1
        return next_id

    def get_app_user(self, username):
        if username not in self.app_user:
            message = 'app_user (username={}) does not exist'.format(username)
            raise KeyError(message)
        app_user = self.app_user[username]
        return copy.copy(app_user)

    def add_app_user(self, app_user):
        if app_user.username in self.app_user:
            message = 'app_user (username={}) already exists'.format(app_user.username)
            raise ValueError(message)
        self.app_user[app_user.username] = copy.copy(app_user)

    def exists_app_user(self, username):
        return (username in self.app_user)
