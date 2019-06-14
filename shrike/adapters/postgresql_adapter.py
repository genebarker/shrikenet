import os

import psycopg2 as driver

from shrike.entities.storage_provider import StorageProvider

class PostgreSQLAdapter(StorageProvider):

    SCHEMA_FILENAME = 'postgresql_schema.sql'
    RESET_FILENAME = 'postgresql_reset.sql'
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

    def initialize_database(self):
        self.rollback()
        self._execute_sql_file(self.SCHEMA_FILENAME)
        self.commit()

    def _execute_sql_file(self, filename):
        file_path = self._get_sql_file_path(filename)
        with self.connection.cursor() as cursor:
            sql_file = open(file_path, 'r')
            cursor.execute(sql_file.read())

    def _get_sql_file_path(self, filename):
        dir_path = os.path.dirname(__file__)
        return os.path.join(dir_path, filename)

    def reset_database_objects(self):
        self.rollback()
        self._execute_sql_file(self.RESET_FILENAME)
        self.commit()

    def get_version(self):
        with self.connection.cursor() as cursor:
            cursor.execute('SELECT version();')
            version = cursor.fetchone()[0]
            return version
