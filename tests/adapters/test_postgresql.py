from configparser import ConfigParser
import logging

import pytest

from shrike.adapters.postgresql import PostgreSQL
from tests.adapters.test_memory import TestMemory

MODULE_UNDER_TEST = 'shrike.adapters.postgresql'


logging.basicConfig(level=logging.DEBUG)


class TestPostgreSQL(TestMemory):

    @pytest.fixture(scope='class')
    def postgresql(self):
        config = ConfigParser()
        config.read('database.cfg')
        db_config = {
            'db_name': config['development']['db_name'],
            'db_user': config['development']['db_user'],
            'db_password': config['development']['db_password'],
        }
        postgresql = PostgreSQL(db_config)
        postgresql.open()
        postgresql.build_database_schema()
        postgresql.commit()
        yield postgresql
        postgresql.close()

    @pytest.fixture
    def storage_provider(self, postgresql):
        storage_provider = postgresql
        storage_provider.reset_database_objects()
        storage_provider.commit()
        yield storage_provider
        storage_provider.rollback()

    def test_get_version_returns_provider_info(self, storage_provider):
        assert storage_provider.get_version().startswith(
            storage_provider.VERSION_PREFIX)

    BAD_SQL = """
        SELECT count(*)
        FROM non_existant_table t
        WHERE t.color = 'red'
        """
    BAD_ERROR = "can not get red count, reason: "
    BAD_MESSAGE = (
        "can not get red count, reason: relation \"non_existant_table\""
        " does not exist\n"
        "LINE 2: FROM non_existant_table t\n"
        "             ^\n"
        "SELECT count(*)\n"
        "FROM non_existant_table t\n"
        "WHERE t.color = 'red'"
    )

    def test_sql_exception_message_format(self, storage_provider):
        db = storage_provider
        with pytest.raises(Exception) as excinfo:
            db._execute_select_value(self.BAD_SQL, self.BAD_ERROR)

        assert str(excinfo.value) == self.BAD_MESSAGE

    def test_sql_exception_logs_as_warning(self, storage_provider, caplog):
        db = storage_provider
        with pytest.raises(Exception):
            db._execute_select_value(self.BAD_SQL, self.BAD_ERROR)

        assert len(caplog.records) == 1
        log_record = caplog.records[0]
        assert log_record.levelname == 'WARNING'
        assert log_record.name == MODULE_UNDER_TEST
        assert log_record.message == self.BAD_MESSAGE
