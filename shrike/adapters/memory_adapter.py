import copy

from shrike.entities.storage_provider import StorageProvider


class MemoryAdapter(StorageProvider):

    def __init__(self):
        self.app_user = {}

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
