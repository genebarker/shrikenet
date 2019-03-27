import psycopg2 as driver

from shrike.entities.storage_provider import StorageProvider

class PostgreSQLAdapter(StorageProvider):

    VERSION_PREFIX = "PostgreSQL"

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

    def get_version(self):
        with self.connection.cursor() as cursor:
            cursor.execute('SELECT version();')
            version = cursor.fetchone()[0]
            return version
