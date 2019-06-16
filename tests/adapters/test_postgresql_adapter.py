from configparser import ConfigParser

import pytest

from shrike.adapters.postgresql_adapter import PostgreSQLAdapter
from tests.adapters.test_memory_adapter import TestMemoryAdapter

class TestPostgreSQLAdapter(TestMemoryAdapter):

    @pytest.fixture(scope='class')
    def postgresql_adapter(self):
        config = ConfigParser()
        config.read('database.cfg')
        dbname = config['development']['db_name']
        user = config['development']['db_user']
        password = config['development']['db_password']
        postgresql_adapter = PostgreSQLAdapter(dbname, user, password)
        postgresql_adapter.open()
        postgresql_adapter.build_database_schema()
        postgresql_adapter.commit()
        yield postgresql_adapter
        postgresql_adapter.close()

    @pytest.fixture
    def storage_provider(self, postgresql_adapter):
        storage_provider = postgresql_adapter
        storage_provider.reset_database_objects()
        storage_provider.commit()
        yield storage_provider
        storage_provider.rollback()

    def test_get_version_returns_provider_info(self, storage_provider):
        assert storage_provider.get_version().startswith(storage_provider.VERSION_PREFIX)

