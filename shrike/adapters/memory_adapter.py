import copy

from shrike.entities.storage_provider import StorageProvider


class MemoryAdapter(StorageProvider):

    VERSION_PREFIX = 'MemoryStore'
    VERSION_NUMBER = '1.0'

    def __init__(self):
        self.app_user = {}
        self.app_user_next_oid = 1
        self.post = {}
        self.post_next_oid = 1
        self.is_open = False

    def save_tables(self):
        self.saved_app_user = {}
        self.saved_post = {}
        for key, value in self.app_user.items():
            self.saved_app_user[key] = copy.copy(value)
        for key, value in self.post.items():
            self.saved_post[key] = copy.copy(value)

    def restore_tables(self):
        self.app_user = {}
        self.post = {}
        for key, value in self.saved_app_user.items():
            self.app_user[key] = copy.copy(value)
        for key, value in self.saved_post.items():
            self.post[key] = copy.copy(value)

    # restrict access to attributes when closed
    def __getattribute__(self, name):
        if (name not in ('open', 'is_open') and not self.is_open):
            error = '{} is not available since the connection is closed'.format(name)
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
        return ('{0} {1} - a lightweight in-memory database for unit testing'
                .format(self.VERSION_PREFIX, self.VERSION_NUMBER))
        
    def get_next_app_user_oid(self):
        next_oid = self.app_user_next_oid
        self.app_user_next_oid += 1
        return next_oid

    def get_next_post_oid(self):
        next_oid = self.post_next_oid
        self.post_next_oid += 1
        return next_oid

    def get_app_user_by_username(self, username):
        oid = self._get_app_user_oid_for_username(username)
        if oid is None:
            message = 'can not get app_user (username={}), reason: record does not exist'.format(username)
            raise KeyError(message)
        return self.get_app_user_by_oid(oid)

    def get_app_user_by_oid(self, oid):
        if oid not in self.app_user:
            message = 'can not get app_user (oid={}), reason: record does not exist'.format(oid)
            raise KeyError(message)
        app_user = self.app_user[oid]
        return copy.copy(app_user)

    def _get_app_user_oid_for_username(self, username):
        for oid, app_user in self.app_user.items():
            if app_user.username == username: return oid
        return None

    def add_app_user(self, app_user):
        error = 'can not add app_user (oid={}, username={}), reason: '.format(app_user.oid, app_user.username)
        if self.exists_app_username(app_user.username):
            reason = 'record with this username already exists'
            raise ValueError(error + reason)
        if app_user.oid in self.app_user:
            reason = 'record with this oid already exists'
            raise ValueError(error + reason)
        self.app_user[app_user.oid] = copy.copy(app_user)

    def update_app_user(self, app_user):
        self.app_user[app_user.oid] = copy.copy(app_user)
    
    def exists_app_username(self, username):
        return self._get_app_user_oid_for_username(username) is not None

    def get_post_by_oid(self, oid):
        if oid not in self.post:
            message = 'can not get post (oid={}), reason: record does not exist'.format(oid)
            raise KeyError(message)
        post = self.post[oid]
        return copy.copy(post)

    def add_post(self, post):
        if post.oid in self.post:
            message = 'can not add post (oid={}, title={}), reason: record with this oid already exists'.format(post.oid, post.title)
            raise ValueError(message)
        self.post[post.oid] = copy.copy(post)

    def update_post(self, post):
        self.post[post.oid] = copy.copy(post)
