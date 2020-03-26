from configparser import ConfigParser

import pytest

from shrike.adapters.postgresql_adapter import PostgreSQLAdapter
from tests.adapters.test_memory_adapter import TestMemoryAdapter


class TestPostgreSQLAdapter(TestMemoryAdapter):

    @pytest.fixture(scope='class')
    def postgresql_adapter(self):
        config = ConfigParser()
        config.read('database.cfg')
        db_config = {
            'db_name': config['development']['db_name'],
            'db_user': config['development']['db_user'],
            'db_password': config['development']['db_password'],
        }
        postgresql_adapter = PostgreSQLAdapter(db_config)
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
        assert storage_provider.get_version().startswith(
            storage_provider.VERSION_PREFIX)

    def test_sql_exception_message_format(self, storage_provider):
        db = storage_provider
        sql = """
            SELECT count(*)
            FROM non_existant_table t
            WHERE t.color = 'red'
            """
        error = "can not get red count, reason: "
        with pytest.raises(Exception) as excinfo:
            db._execute_select_value(sql, error)

        assert str(excinfo.value) == (
            "can not get red count, reason: relation \"non_existant_table\""
            " does not exist\n"
            "LINE 2: FROM non_existant_table t\n"
            "             ^\n"
            "SELECT count(*)\n"
            "FROM non_existant_table t\n"
            "WHERE t.color = 'red'"
        )
