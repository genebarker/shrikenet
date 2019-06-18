import os

import psycopg2 as driver

from shrike.entities.app_user import AppUser
from shrike.entities.post import Post
from shrike.entities.storage_provider import StorageProvider

class PostgreSQLAdapter(StorageProvider):

    SCHEMA_FILENAME = 'pg_build_schema.sql'
    RESET_FILENAME = 'pg_reset_objects.sql'
    VERSION_PREFIX = 'PostgreSQL'

    def __init__(self, db_name, db_user, db_password):
        self.connection = None
        self.__db_name = db_name
        self.__db_user = db_user
        self.__db_password = db_password

    def open(self):
        if self.connection is not None:
            raise Exception('connection already open')
        self.connection = driver.connect(
            dbname=self.__db_name,
            user=self.__db_user,
            password=self.__db_password
            )

    def close(self):
        self.connection.close()
        self.connection = None

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def build_database_schema(self):
        self._execute_sql_file(self.SCHEMA_FILENAME)

    def _execute_sql_file(self, filename):
        file_path = self._get_sql_file_path(filename)
        with self.connection.cursor() as cursor:
            sql_file = open(file_path, 'r')
            cursor.execute(sql_file.read())

    def _get_sql_file_path(self, filename):
        dir_path = os.path.dirname(__file__)
        return os.path.join(dir_path, filename)

    def reset_database_objects(self):
        self._execute_sql_file(self.RESET_FILENAME)

    def get_version(self):
        sql = "SELECT version()"
        error = "can not get version information, reason: "
        return self._execute_select_value(sql, error)

    def _execute_select_value(self, sql, error, parms=None):
        try:
            return self._select_value(sql, parms)
        except Exception as e:
            reason = str(e)
            raise type(e)(error + reason)

    def _select_value(self, sql, parms):
        with self.connection.cursor() as cursor:
            cursor.execute(sql, parms)
            value = cursor.fetchone()[0]
            return value

    def get_next_app_user_oid(self):
        sql = "SELECT nextval('app_user_seq')"
        error = "can not get next app_user oid, reason: "
        return self._execute_select_value(sql, error)

    def get_next_post_oid(self):
        sql = "SELECT nextval('post_seq')"
        error = "can not get next post oid, reason: "
        return self._execute_select_value(sql, error)

    def get_app_user_by_username(self, username):
        sql = "SELECT * FROM app_user WHERE username = %s"
        parms = (username,)
        error = 'can not get app_user (username={}), reason: '.format(username)
        row = self._execute_select_row(sql, parms, error)
        return self._create_app_user_from_row(row)

    def _execute_select_row(self, sql, parms, error):
        try:
            return self._select_row(sql, parms)
        except Exception as e:
            reason = str(e)
            raise type(e)(error + reason)

    def _select_row(self, sql, parms):
        with self.connection.cursor() as cursor:
            cursor.execute(sql, parms)
            row = cursor.fetchone()
            if row is None: raise KeyError('record does not exist')
            return row

    def _create_app_user_from_row(self, row):
        app_user = AppUser(row[0], row[1], row[2], row[3])
        return app_user

    def get_app_user_by_oid(self, oid):
        sql = "SELECT * FROM app_user WHERE oid = %s"
        parms = (oid,)
        error = 'can not get app_user (oid={}), reason: '.format(oid)
        row = self._execute_select_row(sql, parms, error)
        return self._create_app_user_from_row(row)

    def add_app_user(self, app_user):
        sql = "INSERT INTO app_user (oid, username, name, password_hash) VALUES(%s, %s, %s, %s)"
        parms = (app_user.oid, app_user.username, app_user.name, app_user.password_hash)
        error = 'can not add app_user (oid={}, username={}), reason: '.format(app_user.oid, app_user.username)
        self._execute_process_sql(sql, parms, error)

    def _execute_process_sql(self, sql, parms, error):
        try:
            return self._process_sql(sql, parms)
        except Exception as e:
            reason = str(e)
            raise type(e)(error + reason)

    def _process_sql(self, sql, parms):
        with self.connection.cursor() as cursor:
            cursor.execute(sql, parms)

    def update_app_user(self, app_user):
        sql = "UPDATE app_user SET username = %s, name = %s, password_hash = %s WHERE oid = %s"
        parms = (app_user.username, app_user.name, app_user.password_hash, app_user.oid)
        error = 'can not update app_user (oid={}), reason: '.format(app_user.oid)
        self._execute_process_sql(sql, parms, error)

    def exists_app_username(self, username):
        sql = "SELECT count(*) FROM app_user WHERE username = %s"
        parms = (username,)
        error = 'can not check if app_user exists (username={}), reason: '.format(username)
        return self._execute_select_value(sql, error, parms) == 1

    def get_post_by_oid(self, oid):
        sql = "SELECT * FROM post WHERE oid = %s"
        parms = (oid,)
        error = 'can not get post (oid={}), reason: '.format(oid)
        row = self._execute_select_row(sql, parms, error)
        return self._create_post_from_row(row)

    def _create_post_from_row(self, row):
        post = Post(
            oid=row[0],
            title=row[1],
            body=row[2],
            author_oid=row[3],
            created_time=row[4],
            )
        return post

    def add_post(self, post):
        sql = "INSERT INTO post (oid, title, body, author_oid, created_time) VALUES(%s, %s, %s, %s, %s)"
        parms = (post.oid, post.title, post.body, post.author_oid, post.created_time)
        error = 'can not add post (oid={}, title={}), reason: '.format(post.oid, post.title)
        self._execute_process_sql(sql, parms, error)

    def update_post(self, post):
        sql = "UPDATE post SET title = %s, body = %s, author_oid = %s, created_time = %s WHERE oid = %s"
        parms = (post.title, post.body, post.author_oid, post.created_time, post.oid)
        error = 'can not update post (oid={}), reason: '.format(post.oid)
        self._execute_process_sql(sql, parms, error)
