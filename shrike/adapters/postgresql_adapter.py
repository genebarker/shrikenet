import psycopg2 as driver

from shrike.entities.storage_provider import StorageProvider

class PostgreSQLAdapter(StorageProvider):

    def __init__(self, db_name, db_user, db_password):
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.connection = None

    def open(self):
        self.connection = driver.connect(
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password
            )

    def close(self):
        self.connection.close()

    def get_version(self):
        with self.connection.cursor() as cursor:
            cursor.execute('SELECT version();')
            version = cursor.fetchone()[0]
            return version
