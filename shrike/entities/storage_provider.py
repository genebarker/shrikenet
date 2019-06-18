from abc import ABC, abstractmethod

class StorageProvider(ABC):

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass

    @abstractmethod
    def build_database_schema(self):
        pass

    @abstractmethod
    def reset_database_objects(self):
        pass

    @abstractmethod
    def get_version(self):
        pass

    @abstractmethod
    def get_next_app_user_oid(self):
        pass

    @abstractmethod
    def get_next_post_oid(self):
        pass

    @abstractmethod
    def get_app_user_by_username(self, username):
        pass

    @abstractmethod
    def get_app_user_by_oid(self, oid):
        pass

    @abstractmethod
    def add_app_user(self, app_user):
        pass
    
    @abstractmethod
    def update_app_user(self, app_user):
        pass

    @abstractmethod
    def exists_app_username(self, username):
        pass

    @abstractmethod
    def get_post_by_oid(self, oid):
        pass

    @abstractmethod
    def add_post(self, post):
        pass

    @abstractmethod
    def update_post(self, post):
        pass
