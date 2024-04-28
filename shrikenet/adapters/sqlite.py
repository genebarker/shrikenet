from datetime import datetime
import inspect
import logging
import os
import sqlite3
from shrikenet.entities.exceptions import (
    DatastoreAlreadyOpen,
    DatastoreClosed,
    DatastoreError,
    DatastoreKeyError,
)
from shrikenet.entities.app_user import AppUser
from shrikenet.entities.post import Post, DeepPost
from shrikenet.entities.rules import Rules
from shrikenet.entities.storage_provider import StorageProvider


class SQLite(StorageProvider):

    SCHEMA_FILENAME = "build_schema.sql"
    RESET_FILENAME = "reset_objects.sql"

    def __init__(self, db_file):
        self.is_open = False
        self.connection = None
        self.logger = logging.getLogger(__name__)
        self.db_file = db_file

    def open(self):
        if self.is_open:
            raise DatastoreAlreadyOpen("connection already open")
        self.connection = sqlite3.connect(self.db_file)
        self.is_open = True

    def close(self):
        if not self.is_open:
            raise DatastoreClosed("connection already closed")
        self.connection.close()  # not reset to None, let SQLite handle state
        self.is_open = False

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def build_database_schema(self):
        self._execute_sql_file(self.SCHEMA_FILENAME)

    def _execute_sql_file(self, filename):
        file_path = self._get_sql_file_path(filename)
        with open(file_path) as sql_file:
            self.connection.executescript(sql_file.read())

    def _get_sql_file_path(self, filename):
        dir_path = os.path.dirname(__file__)
        return os.path.join(dir_path, filename)

    def reset_database_objects(self):
        self._execute_sql_file(self.RESET_FILENAME)

    def get_version(self):
        sql = "SELECT sqlite_version()"
        parms = []
        error = "can not get version information, reason: "
        version_num = self._execute_select_value(sql, parms, error)
        return f"SQLite version {version_num}"

    def _execute_select_value(self, sql, parms, error):
        return self._execute_select("_select_value", sql, parms, error)

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
        cursor = self.connection.execute(sql, parms)
        value = cursor.fetchone()[0]
        return value

    def get_app_user_by_username(self, username):
        sql = "SELECT * FROM app_user WHERE username = ?"
        parms = [
            username,
        ]
        error = f"can not get app_user (username={username}), reason: "
        row = self._execute_select_row(sql, parms, error)
        app_user = self._create_app_user_from_row(row)
        return app_user

    def _execute_select_row(self, sql, parms, error):
        return self._execute_select("_select_row", sql, parms, error)

    def _select_row(self, sql, parms):
        cursor = self.connection.execute(sql, parms)
        row = cursor.fetchone()
        if row is None:
            raise DatastoreKeyError("record does not exist")
        return row

    def _create_app_user_from_row(self, row):
        app_user = AppUser(
            oid=row[0],
            username=row[1],
            name=row[2],
            password_hash=row[3],
            needs_password_change=self.sql_to_bool(row[4]),
            is_locked=self.sql_to_bool(row[5]),
            is_dormant=self.sql_to_bool(row[6]),
            ongoing_password_failure_count=row[7],
            last_password_failure_time=self.sql_to_datetime(row[8]),
        )
        return app_user

    def sql_to_bool(self, sql_bool):
        if sql_bool == "true":
            return True
        return False

    def sql_to_datetime(self, sql_datetime):
        if sql_datetime is None:
            return None
        return datetime.strptime(sql_datetime, "%Y-%m-%d %H:%M:%S.%f")

    def get_app_user_by_oid(self, oid):
        sql = "SELECT * FROM app_user WHERE oid = ?"
        parms = [
            oid,
        ]
        error = f"can not get app_user (oid={oid}), reason: "
        row = self._execute_select_row(sql, parms, error)
        app_user = self._create_app_user_from_row(row)
        return app_user

    def add_app_user(self, app_user):
        sql = """
            INSERT INTO app_user (username, name, password_hash,
                needs_password_change, is_locked, is_dormant,
                ongoing_password_failure_count,
                last_password_failure_time)
            VALUES
                (?, ?, ?, ?, ?, ?, ?, ?)
        """
        parms = [
            app_user.username,
            app_user.name,
            app_user.password_hash,
            self.bool_to_sql(app_user.needs_password_change),
            self.bool_to_sql(app_user.is_locked),
            self.bool_to_sql(app_user.is_dormant),
            app_user.ongoing_password_failure_count,
            self.datetime_to_sql(app_user.last_password_failure_time),
        ]
        error = (
            f"can not add app_user (username={app_user.username}), reason: "
        )
        oid = self._execute_insert_and_get_oid(sql, parms, error)
        return oid

    def bool_to_sql(self, py_bool):
        if py_bool:
            return "true"
        return "false"

    def datetime_to_sql(self, py_datetime):
        if py_datetime is None:
            return None
        return py_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")

    def _execute_insert_and_get_oid(self, sql, parms, error):
        clean_sql = inspect.cleandoc(sql)
        try:
            cursor = self.connection.execute(clean_sql, parms)
            oid = cursor.lastrowid
            return oid
        except Exception as e:
            self._process_exception(e, error, clean_sql)

    def update_app_user(self, app_user):
        sql = """
            UPDATE app_user
            SET username = ?,
                name = ?,
                password_hash = ?,
                needs_password_change = ?,
                is_locked = ?,
                is_dormant = ?,
                ongoing_password_failure_count = ?,
                last_password_failure_time = ?
            WHERE oid = ?
        """
        parms = [
            app_user.username,
            app_user.name,
            app_user.password_hash,
            self.bool_to_sql(app_user.needs_password_change),
            self.bool_to_sql(app_user.is_locked),
            self.bool_to_sql(app_user.is_dormant),
            app_user.ongoing_password_failure_count,
            self.datetime_to_sql(app_user.last_password_failure_time),
            app_user.oid,
        ]
        error = f"can not update app_user (oid={app_user.oid}), reason: "
        self._execute_update_row(sql, parms, error)

    def _execute_update_row(self, sql, parms, error):
        clean_sql = inspect.cleandoc(sql)
        try:
            cursor = self.connection.execute(clean_sql, parms)
            if cursor.rowcount == 0:
                raise KeyError("record does not exist")
            if cursor.rowcount > 1:
                raise Exception("sql affected more than one record")
        except Exception as e:
            self._process_exception(e, error, clean_sql)

    def get_app_user_count(self):
        sql = "SELECT count(*) FROM app_user"
        parms = []
        error = "can not get count of app_user records, reason: "
        return self._execute_select_value(sql, parms, error)

    def exists_app_username(self, username):
        sql = "SELECT count(*) FROM app_user WHERE username = ?"
        parms = [
            username,
        ]
        error = f"can not check if app_user exists (username={username}), reason: "
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
            WHERE p.oid = ?
        """
        parms = [
            oid,
        ]
        error = f"can not get post (oid={oid}), reason: "
        row = self._execute_select_row(sql, parms, error)
        post = self._create_deep_post_from_row(row)
        return post

    def _create_deep_post_from_row(self, row):
        post = Post(
            oid=row[0],
            title=row[1],
            body=row[2],
            author_oid=row[3],
            created_time=self.sql_to_datetime(row[4]),
        )
        author_username = row[5]
        return DeepPost(post, author_username)

    def add_post(self, post):
        sql = """
            INSERT INTO post (title, body, author_oid, created_time)
            VALUES (?, ?, ?, ?)
        """
        parms = [
            post.title,
            post.body,
            post.author_oid,
            self.datetime_to_sql(post.created_time),
        ]
        error = f"can not add post (title={post.title}), reason: "
        oid = self._execute_insert_and_get_oid(sql, parms, error)
        return oid

    def update_post(self, post):
        sql = """
            UPDATE post
            SET title = ?,
                body = ?,
                author_oid = ?,
                created_time = ?
            WHERE oid = ?
        """
        parms = [
            post.title,
            post.body,
            post.author_oid,
            self.datetime_to_sql(post.created_time),
            post.oid,
        ]
        error = "can not update post (oid={}), reason: ".format(post.oid)
        self._execute_update_row(sql, parms, error)

    def delete_post_by_oid(self, oid):
        sql = "DELETE FROM post WHERE oid = ?"
        parms = [
            oid,
        ]
        error = "can not delete post (oid={}), reason: ".format(oid)
        self._execute_update_row(sql, parms, error)

    def get_post_count(self):
        sql = "SELECT count(*) FROM post"
        parms = []
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
        parms = []
        error = "can not get posts, reason: "
        rows = self._execute_select_all_rows(sql, parms, error)
        posts = []
        for row in rows:
            posts.append(self._create_deep_post_from_row(row))
        return posts

    def _execute_select_all_rows(self, sql, parms, error):
        return self._execute_select("_select_all_rows", sql, parms, error)

    def _select_all_rows(self, sql, parms):
        cursor = self.connection.execute(sql, parms)
        return cursor.fetchall()

    def get_rules(self):
        sql = "SELECT tag, tag_value, tag_type FROM rule"
        parms = []
        error = "can not get rules, reason: "
        rows = self._execute_select_all_rows(sql, parms, error)
        rules = Rules()
        for row in rows:
            tag = row[0]
            tag_type = row[2]
            tag_value = int(row[1]) if tag_type == "int" else row[1]
            setattr(rules, tag, tag_value)
        return rules

    def save_rules(self, rules):
        sql = "DELETE FROM rule"
        parms = []
        error = "can not save rules, reason: "
        self._execute_sql(sql, parms, error)

        attribute = {
            "login_fail_threshold_count": "int",
            "login_fail_lock_minutes": "int",
        }
        for key, value in attribute.items():
            sql = """
                INSERT INTO rule (tag, tag_value, tag_type)
                VALUES (?, ?, ?)
            """
            tag = key
            tag_type = value
            tag_value = str(getattr(rules, tag))
            parms = (tag, tag_value, tag_type)
            self._execute_sql(sql, parms, error)

    def _execute_sql(self, sql, parms, error):
        clean_sql = inspect.cleandoc(sql)
        try:
            self.connection.execute(clean_sql, parms)
        except Exception as e:
            self._process_exception(e, error, clean_sql)
