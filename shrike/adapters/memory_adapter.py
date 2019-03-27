import copy

from shrike.entities.storage_provider import StorageProvider


class MemoryAdapter(StorageProvider):

    VERSION_PREFIX = "HomeBrewed"

    def __init__(self):
        self.app_user = {}
        self.is_open = False

    def verify_open(self):
        if self.is_open:
            return
        raise Exception('connection closed')

    def open(self):
        if self.is_open:
            raise Exception('connection already open')
        self.is_open = True

    def close(self):
        self.verify_open()
        self.is_open = False

    def commit(self):
        self.verify_open()
        pass

    def rollback(self):
        self.verify_open()
        pass

    def get_version(self):
        self.verify_open()
        return self.VERSION_PREFIX

    def get_app_user(self, username):
        self.verify_open()
        if username not in self.app_user:
            message = 'app_user (username={}) does not exist'.format(username)
            raise KeyError(message)
        app_user = self.app_user[username]
        return copy.copy(app_user)

    def add_app_user(self, app_user):
        self.verify_open()
        if app_user.username in self.app_user:
            message = 'app_user (username={}) already exists'.format(app_user.username)
            raise ValueError(message)
        self.app_user[app_user.username] = copy.copy(app_user)

    def exists_app_user(self, username):
        self.verify_open()
        return (username in self.app_user)
