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
from shrikenet.entities.log_entry import LogEntry
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
