class StorageProvider:

    def __init__(self, db_config):
        raise NotImplementedError

    def open(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def commit(self):
        raise NotImplementedError

    def rollback(self):
        raise NotImplementedError

    def build_database_schema(self):
        raise NotImplementedError

    def reset_database_objects(self):
        raise NotImplementedError

    def get_version(self):
        raise NotImplementedError

    def get_next_app_user_oid(self):
        raise NotImplementedError

    def get_next_post_oid(self):
        raise NotImplementedError

    def get_app_user_by_username(self, username):
        raise NotImplementedError

    def get_app_user_by_oid(self, oid):
        raise NotImplementedError

    def add_app_user(self, app_user):
        raise NotImplementedError

    def update_app_user(self, app_user):
        raise NotImplementedError

    def get_app_user_count(self):
        raise NotImplementedError

    def exists_app_username(self, username):
        raise NotImplementedError

    def get_post_by_oid(self, oid):
        raise NotImplementedError

    def add_post(self, post):
        raise NotImplementedError

    def update_post(self, post):
        raise NotImplementedError

    def delete_post_by_oid(self, oid):
        raise NotImplementedError

    def get_post_count(self):
        raise NotImplementedError

    def get_posts(self):
        raise NotImplementedError

    def get_rules(self):
        raise NotImplementedError

    def save_rules(self, parameters):
        raise NotImplementedError
