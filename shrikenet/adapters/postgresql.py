import inspect
import logging
import os

import psycopg2 as driver

from shrikenet.entities.app_user import AppUser
from shrikenet.entities.exceptions import (
    DatastoreAlreadyOpen,
    DatastoreError,
    DatastoreKeyError,
)
from shrikenet.entities.post import DeepPost, Post
from shrikenet.entities.rules import Rules
from shrikenet.entities.storage_provider import StorageProvider


class PostgreSQL(StorageProvider):

    SCHEMA_FILENAME = 'pg_build_schema.sql'
    RESET_FILENAME = 'pg_reset_objects.sql'
    VERSION_PREFIX = 'PostgreSQL'

    def __init__(self, db_config):
        self.connection = None
        self.__db_name = db_config['db_name']
        self.__db_user = db_config['db_user']
        self.__db_password = db_config['db_password']
        self.__db_port = db_config['db_port']
        self.logger = logging.getLogger(__name__)

    def open(self):
        if self.connection is not None:
            raise DatastoreAlreadyOpen('connection already open')
        self.connection = driver.connect(
            dbname=self.__db_name,
            user=self.__db_user,
            password=self.__db_password,
            port=self.__db_port,
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
        with open(file_path) as sql_file:
            with self.connection.cursor() as cursor:
                cursor.execute(sql_file.read())

    def _get_sql_file_path(self, filename):
        dir_path = os.path.dirname(__file__)
        return os.path.join(dir_path, filename)

    def reset_database_objects(self):
        self._execute_sql_file(self.RESET_FILENAME)

    def get_version(self):
        sql = "SELECT version()"
        parms = None
        error = 'can not get version information, reason: '
        return self._execute_select_value(sql, parms, error)

    def _execute_select_value(self, sql, parms, error):
        return self._execute_select('_select_value', sql, parms, error)

    def _execute_select(self, function_name, sql, parms, error):
        clean_sql = inspect.cleandoc(sql)
        func = getattr(self, function_name)
        try:
            return func(clean_sql, parms)
        except Exception as e:
            self._process_exception(e, error, clean_sql)

    def _process_exception(self, exception, error, sql):
        reason = str(exception)
        message = self._compose_error_message(error, reason, sql)
        self.logger.warning(message)
        if isinstance(exception, KeyError):
            raise DatastoreKeyError(message) from exception
        raise DatastoreError(message) from exception

    def _compose_error_message(self, error, reason, sql):
        return (error + reason).strip() + "\n" + sql

    def _select_value(self, sql, parms):
        with self.connection.cursor() as cursor:
            cursor.execute(sql, parms)
            value = cursor.fetchone()[0]
            return value

    def get_next_app_user_oid(self):
        sql = "SELECT nextval('app_user_seq')"
        parms = None
        error = 'can not get next app_user oid, reason: '
        return self._execute_select_value(sql, parms, error)

    def get_next_event_oid(self):
        sql = "SELECT nextval('event_seq')"
        parms = None
        error = 'can not get next event oid, reason: '
        return self._execute_select_value(sql, parms, error)

    def get_next_post_oid(self):
        sql = "SELECT nextval('post_seq')"
        parms = None
        error = 'can not get next post oid, reason: '
        return self._execute_select_value(sql, parms, error)

    def get_app_user_by_username(self, username):
        sql = "SELECT * FROM app_user WHERE username = %s"
        parms = (username,)
        error = 'can not get app_user (username={}), reason: '.format(username)
        row = self._execute_select_row(sql, parms, error)
        return self._create_app_user_from_row(row)

    def _execute_select_row(self, sql, parms, error):
        return self._execute_select('_select_row', sql, parms, error)

    def _select_row(self, sql, parms):
        with self.connection.cursor() as cursor:
            cursor.execute(sql, parms)
            row = cursor.fetchone()
            if row is None:
                raise DatastoreKeyError('record does not exist')
            return row

    def _create_app_user_from_row(self, row):
        app_user = AppUser(
            oid=row[0],
            username=row[1],
            name=row[2],
            password_hash=row[3],
            needs_password_change=row[4],
            is_locked=row[5],
            is_dormant=row[6],
            ongoing_password_failure_count=row[7],
            last_password_failure_time=row[8],
        )
        return app_user

    def get_app_user_by_oid(self, oid):
        sql = "SELECT * FROM app_user WHERE oid = %s"
        parms = (oid,)
        error = 'can not get app_user (oid={}), reason: '.format(oid)
        row = self._execute_select_row(sql, parms, error)
        return self._create_app_user_from_row(row)

    def add_app_user(self, app_user):
        sql = """
            INSERT INTO app_user (
                oid,
                username,
                name,
                password_hash,
                needs_password_change,
                is_locked,
                is_dormant,
                ongoing_password_failure_count,
                last_password_failure_time
            )
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        parms = (
            app_user.oid,
            app_user.username,
            app_user.name,
            app_user.password_hash,
            app_user.needs_password_change,
            app_user.is_locked,
            app_user.is_dormant,
            app_user.ongoing_password_failure_count,
            app_user.last_password_failure_time,
        )
        error = (
            'can not add app_user (oid={}, username={}), reason: '
            .format(app_user.oid, app_user.username)
        )
        self._execute_process_sql(sql, parms, error)

    def _execute_process_sql(self, sql, parms, error):
        clean_sql = inspect.cleandoc(sql)
        try:
            return self._process_sql(clean_sql, parms)
        except Exception as e:
            self._process_exception(e, error, clean_sql)

    def _process_sql(self, sql, parms):
        with self.connection.cursor() as cursor:
            cursor.execute(sql, parms)

    def update_app_user(self, app_user):
        sql = """
            UPDATE app_user
            SET username = %s,
                name = %s,
                password_hash = %s,
                needs_password_change = %s,
                is_locked = %s,
                is_dormant = %s,
                ongoing_password_failure_count = %s,
                last_password_failure_time = %s
            WHERE oid = %s
        """
        parms = (
            app_user.username,
            app_user.name,
            app_user.password_hash,
            app_user.needs_password_change,
            app_user.is_locked,
            app_user.is_dormant,
            app_user.ongoing_password_failure_count,
            app_user.last_password_failure_time,
            app_user.oid,
        )
        error = (
            'can not update app_user (oid={}), reason: '
            .format(app_user.oid)
        )
        self._execute_process_sql(sql, parms, error)

    def get_app_user_count(self):
        sql = "SELECT count(*) FROM app_user"
        parms = None
        error = 'can not get count of app_user records, reason: '
        return self._execute_select_value(sql, parms, error)

    def exists_app_username(self, username):
        sql = "SELECT count(*) FROM app_user WHERE username = %s"
        parms = (username,)
        error = (
            'can not check if app_user exists (username={}), reason: '
            .format(username)
        )
        return self._execute_select_value(sql, parms, error) == 1

    def get_post_by_oid(self, oid):
        sql = """
            SELECT p.oid,
                p.title,
                p.body,
                p.author_oid,
                p.created_time,
                u.username AS author_username
            FROM post p
            LEFT OUTER JOIN app_user u
            ON p.author_oid = u.oid
            WHERE p.oid = %s
        """
        parms = (oid,)
        error = 'can not get post (oid={}), reason: '.format(oid)
        row = self._execute_select_row(sql, parms, error)
        return self._create_deep_post_from_row(row)

    def _create_deep_post_from_row(self, row):
        post = Post(
            oid=row[0],
            title=row[1],
            body=row[2],
            author_oid=row[3],
            created_time=row[4],
            )
        return DeepPost(post, row[5])

    def add_post(self, post):
        sql = """
            INSERT INTO post (oid, title, body, author_oid, created_time)
            VALUES(%s, %s, %s, %s, %s)
        """
        parms = (
            post.oid,
            post.title,
            post.body,
            post.author_oid,
            post.created_time,
        )
        error = (
            'can not add post (oid={}, title={}), reason: '
            .format(post.oid, post.title)
        )
        self._execute_process_sql(sql, parms, error)

    def update_post(self, post):
        sql = """
            UPDATE post
            SET title = %s,
                body = %s,
                author_oid = %s,
                created_time = %s
            WHERE oid = %s
        """
        parms = (
            post.title,
            post.body,
            post.author_oid,
            post.created_time,
            post.oid,
        )
        error = 'can not update post (oid={}), reason: '.format(post.oid)
        self._execute_process_sql(sql, parms, error)

    def delete_post_by_oid(self, oid):
        sql = "DELETE FROM post WHERE oid = %s"
        parms = (oid,)
        error = 'can not delete post (oid={}), reason: '.format(oid)
        self._execute_process_sql(sql, parms, error)

    def get_post_count(self):
        sql = "SELECT count(*) FROM post"
        parms = None
        error = "can not get count of post records, reason: "
        return self._execute_select_value(sql, parms, error)

    def get_posts(self):
        sql = """
            SELECT p.oid,
                p.title,
                p.body,
                p.author_oid,
                p.created_time,
                u.username AS author_username
            FROM post p
            LEFT OUTER JOIN app_user u ON p.author_oid = u.oid
            ORDER BY p.created_time DESC
        """
        parms = None
        error = 'can not get posts, reason: '
        rows = self._execute_select_all_rows(sql, parms, error)
        posts = []
        for row in rows:
            posts.append(self._create_deep_post_from_row(row))
        return posts

    def _execute_select_all_rows(self, sql, parms, error):
        return self._execute_select('_select_all_rows', sql, parms, error)

    def _select_all_rows(self, sql, parms):
        with self.connection.cursor() as cursor:
            cursor.execute(sql, parms)
            return cursor.fetchall()

    def get_rules(self):
        sql = "SELECT tag, tag_value, tag_type FROM rule"
        parms = None
        error = 'can not get rules, reason: '
        rows = self._execute_select_all_rows(sql, parms, error)
        rules = Rules()
        for row in rows:
            tag = row[0]
            tag_type = row[2]
            tag_value = int(row[1]) if tag_type == 'int' else row[1]
            setattr(rules, tag, tag_value)
        return rules

    def save_rules(self, rules):
        sql = "DELETE FROM rule"
        parms = None
        error = 'can not save rules, reason: '
        self._execute_process_sql(sql, parms, error)

        attribute = {
            'login_fail_threshold_count': 'int',
            'login_fail_lock_minutes': 'int',
        }
        for key, value in attribute.items():
            sql = """
                INSERT INTO rule (tag, tag_value, tag_type)
                VALUES (%s, %s, %s)
            """
            tag = key
            tag_type = value
            tag_value = str(getattr(rules, tag))
            parms = (tag, tag_value, tag_type)
            self._execute_process_sql(sql, parms, error)
