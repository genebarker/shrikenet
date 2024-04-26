from datetime import datetime
import inspect
import logging
import os
import sqlite3
from shrikenet.entities.exceptions import (
    DatastoreAlreadyOpen,
    DatastoreError,
    DatastoreKeyError,
)
from shrikenet.entities.app_user import AppUser
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
        self.connection.close()

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
        parms = (
            app_user.username,
            app_user.name,
            app_user.password_hash,
            self.bool_to_sql(app_user.needs_password_change),
            self.bool_to_sql(app_user.is_locked),
            self.bool_to_sql(app_user.is_dormant),
            app_user.ongoing_password_failure_count,
            self.datetime_to_sql(app_user.last_password_failure_time),
            app_user.oid,
        )
        error = "can not update app_user (oid={}), reason: ".format(
            app_user.oid
        )
        self._execute_sql(sql, parms, error)

    def _execute_sql(self, sql, parms, error):
        clean_sql = inspect.cleandoc(sql)
        try:
            self.connection.execute(clean_sql, parms)
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
