import copy
from operator import attrgetter

from shrike.entities.exceptions import (
    DatastoreClosed,
    DatastoreAlreadyOpen,
)
from shrike.entities.post import DeepPost
from shrike.entities.rules import Rules
from shrike.entities.storage_provider import StorageProvider


class Memory(StorageProvider):

    VERSION_PREFIX = 'MemoryStore'
    VERSION_NUMBER = '1.0'

    def __init__(self, db_config=None):
        self._build_schema()
        self.is_open = False

    def _build_schema(self):
        self.app_user = {}
        self.app_user_next_oid = 1
        self.post = {}
        self.post_next_oid = 1
        self.rules = Rules()

    def save_tables(self):
        self.saved_app_user = {}
        self.saved_post = {}
        for key, value in self.app_user.items():
            self.saved_app_user[key] = copy.copy(value)
        for key, value in self.post.items():
            self.saved_post[key] = copy.copy(value)
        self.saved_rules = copy.copy(self.rules)

    def restore_tables(self):
        self.app_user = {}
        self.post = {}
        for key, value in self.saved_app_user.items():
            self.app_user[key] = copy.copy(value)
        for key, value in self.saved_post.items():
            self.post[key] = copy.copy(value)
        self.rules = copy.copy(self.saved_rules)

    # restrict access to attributes when closed
    def __getattribute__(self, name):
        if (
            name not in ('open', 'is_open', '_build_schema')
            and not self.is_open
        ):
            error = (
                '{} is not available since the connection is closed'
                .format(name)
            )
            raise DatastoreClosed(error)
        return object.__getattribute__(self, name)

    def open(self):
        if self.is_open:
            raise DatastoreAlreadyOpen('connection already open')
        self.is_open = True
        self.save_tables()

    def close(self):
        self.restore_tables()
        self.is_open = False

    def commit(self):
        self.save_tables()

    def rollback(self):
        self.restore_tables()

    def build_database_schema(self):
        self._build_schema()

    def reset_database_objects(self):
        self._build_schema()

    def get_version(self):
        return (
            '{0} {1} - a lightweight in-memory database for unit testing'
            .format(self.VERSION_PREFIX, self.VERSION_NUMBER)
        )

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
            message = (
                'can not get app_user (username={}), reason: record does '
                'not exist'
                .format(username)
            )
            raise KeyError(message)
        return self.get_app_user_by_oid(oid)

    def get_app_user_by_oid(self, oid):
        if oid not in self.app_user:
            message = (
                'can not get app_user (oid={}), reason: record does not '
                'exist'
                .format(oid)
            )
            raise KeyError(message)
        app_user = self.app_user[oid]
        return copy.copy(app_user)

    def _get_app_user_oid_for_username(self, username):
        for oid, app_user in self.app_user.items():
            if app_user.username == username:
                return oid
        return None

    def add_app_user(self, app_user):
        error = (
            'can not add app_user (oid={}, username={}), reason: '
            .format(app_user.oid, app_user.username)
        )
        if self.exists_app_username(app_user.username):
            reason = 'record with this username already exists'
            raise ValueError(error + reason)
        if app_user.oid in self.app_user:
            reason = 'record with this oid already exists'
            raise ValueError(error + reason)
        self.app_user[app_user.oid] = copy.copy(app_user)

    def update_app_user(self, app_user):
        self.app_user[app_user.oid] = copy.copy(app_user)

    def get_app_user_count(self):
        return len(self.app_user)

    def exists_app_username(self, username):
        return self._get_app_user_oid_for_username(username) is not None

    def get_post_by_oid(self, oid):
        if oid not in self.post:
            message = (
                'can not get post (oid={}), reason: record does not exist'
                .format(oid)
            )
            raise KeyError(message)
        post = self.post[oid]
        author = self.app_user[post.author_oid]
        return DeepPost(post, author.username)

    def add_post(self, post):
        if post.oid in self.post:
            message = (
                'can not add post (oid={}, title={}), reason: record with '
                'this oid already exists'
                .format(post.oid, post.title)
            )
            raise ValueError(message)
        self.post[post.oid] = copy.copy(post)

    def update_post(self, post):
        self.post[post.oid] = copy.copy(post)

    def delete_post_by_oid(self, oid):
        del self.post[oid]

    def get_post_count(self):
        return len(self.post)

    def get_posts(self):
        posts = []
        for post in self.post.values():
            author_username = (
                self.app_user[post.author_oid].username
                if post.author_oid in self.app_user
                else None
            )
            posts.append(DeepPost(post, author_username))
        posts.sort(key=attrgetter('created_time'), reverse=True)
        return posts

    def get_rules(self):
        if self.rules is None:
            return None
        return copy.copy(self.rules)

    def save_rules(self, rules):
        self.rules = None if rules is None else copy.copy(rules)
