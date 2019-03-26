from configparser import ConfigParser

from shrike.adapters.postgresql_adapter import PostgreSQLAdapter

class TestPostgreSQLAdapter():

    storage_provider = None

    @classmethod
    def setup_class(cls):
        config = ConfigParser()
        config.read('database.cfg')
        dbname = config['development']['db_name']
        user = config['development']['db_user']
        password = config['development']['db_password']
        cls.storage_provider = PostgreSQLAdapter(dbname, user, password)
        cls.storage_provider.open()

    @classmethod
    def teardown_class(cls):
        cls.storage_provider.close()

    def test_uses_postgresql(self):
        result = self.storage_provider.get_version()
        assert result.startswith('PostgreSQL')
