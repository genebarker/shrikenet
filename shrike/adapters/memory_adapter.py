import copy

from shrike.entities.storage_provider import StorageProvider


class MemoryAdapter(StorageProvider):

    VERSION_PREFIX = "MemoryStore"
    VERSION_NUMBER = "1.0"

    def __init__(self):
        self.app_user = {}
        self.app_user_next_oid = 1
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
        
    def get_next_app_user_oid(self):
        next_oid = self.app_user_next_oid
        self.app_user_next_oid += 1
        return next_oid

    def get_app_user_by_username(self, username):
        oid = self._get_app_user_oid_for_username(username)
        if oid is None:
            message = 'app_user (username={}) does not exist'.format(username)
            raise KeyError(message)
        return self.get_app_user_by_oid(oid)

    def get_app_user_by_oid(self, oid):
        if oid not in self.app_user:
            message = 'app_user (oid={}) does not exist'.format(oid)
            raise KeyError(message)
        app_user = self.app_user[oid]
        return copy.copy(app_user)

    def _get_app_user_oid_for_username(self, username):
        for oid, app_user in self.app_user.items():
            if app_user.username == username: return oid
        return None

    def add_app_user(self, app_user):
        if self.exists_app_username(app_user.username):
            message = 'app_user (username={}) already exists'.format(app_user.username)
            raise ValueError(message)
        if app_user.oid in self.app_user:
            message = 'app_user (oid={}) already exists'.format(app_user.oid)
            raise ValueError(message)
        self.app_user[app_user.oid] = copy.copy(app_user)

    def update_app_user(self, app_user):
        self.app_user[app_user.oid] = copy.copy(app_user)
    
    def exists_app_username(self, username):
        return self._get_app_user_oid_for_username(username) is not None
