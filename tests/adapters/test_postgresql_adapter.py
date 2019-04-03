from configparser import ConfigParser

import pytest

from shrike.adapters.postgresql_adapter import PostgreSQLAdapter

class TestPostgreSQLAdapter():

    storage_provider = None

    @classmethod
    def setup_class(cls):
        cls.storage_provider = cls.get_storage_provider()
        cls.storage_provider.open()

    @staticmethod
    def get_storage_provider():
        config = ConfigParser()
        config.read('database.cfg')
        dbname = config['development']['db_name']
        user = config['development']['db_user']
        password = config['development']['db_password']
        return PostgreSQLAdapter(dbname, user, password)

    @classmethod
    def teardown_class(cls):
        cls.storage_provider.close()
        cls.storage_provider = None

    def test_get_version_aligns_with_provider(self):
        result = self.storage_provider.get_version()
        assert result.startswith('PostgreSQL')

