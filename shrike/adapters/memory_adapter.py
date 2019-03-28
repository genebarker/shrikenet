import copy

from shrike.entities.storage_provider import StorageProvider


class MemoryAdapter(StorageProvider):

    VERSION_PREFIX = "HomeBrewed"

    def __init__(self):
        self.app_user = {}
        self.app_user_next_id = 1
        self.is_open = False

    # restrict access to attributes when closed
    def __getattribute__(self, name):
        if name != 'open' and name != 'is_open' and not self.is_open:
            raise Exception('connection closed')
        return object.__getattribute__(self, name)

    def open(self):
        if self.is_open:
            raise Exception('connection already open')
        self.is_open = True

    def close(self):
        self.is_open = False

    def commit(self):
        pass

    def rollback(self):
        pass

    def get_version(self):
        return self.VERSION_PREFIX

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
