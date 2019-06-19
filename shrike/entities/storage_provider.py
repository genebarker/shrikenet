from abc import ABC, abstractmethod

class StorageProvider(ABC):

    @abstractmethod
    def __init__(self, db_config):
        raise NotImplementedError #pragma: no cover

    @abstractmethod
    def open(self):
        raise NotImplementedError #pragma: no cover

    @abstractmethod
    def close(self):
        raise NotImplementedError #pragma: no cover

    @abstractmethod
    def commit(self):
        raise NotImplementedError #pragma: no cover

    @abstractmethod
    def rollback(self):
        raise NotImplementedError #pragma: no cover

    @abstractmethod
    def build_database_schema(self):
        raise NotImplementedError #pragma: no cover

    @abstractmethod
    def reset_database_objects(self):
        raise NotImplementedError #pragma: no cover

    @abstractmethod
    def get_version(self):
        raise NotImplementedError #pragma: no cover

    @abstractmethod
    def get_next_app_user_oid(self):
        raise NotImplementedError #pragma: no cover

    @abstractmethod
    def get_next_post_oid(self):
        raise NotImplementedError #pragma: no cover

    @abstractmethod
    def get_app_user_by_username(self, username):
        raise NotImplementedError #pragma: no cover

    @abstractmethod
    def get_app_user_by_oid(self, oid):
        raise NotImplementedError #pragma: no cover

    @abstractmethod
    def add_app_user(self, app_user):
        raise NotImplementedError #pragma: no cover
    
    @abstractmethod
    def update_app_user(self, app_user):
        raise NotImplementedError #pragma: no cover

    @abstractmethod
    def exists_app_username(self, username):
        raise NotImplementedError #pragma: no cover

    @abstractmethod
    def get_post_by_oid(self, oid):
        raise NotImplementedError #pragma: no cover

    @abstractmethod
    def add_post(self, post):
        raise NotImplementedError #pragma: no cover

    @abstractmethod
    def update_post(self, post):
        raise NotImplementedError #pragma: no cover

    @abstractmethod
    def get_posts(self):
        raise NotImplementedError #pragma: no cover
