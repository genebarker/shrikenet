import pytest

from shrikenet.adapters.sqlite import SQLite
from shrikenet.entities.exceptions import DatastoreError


DATABASE = "test.db"

BAD_SQL = """
    SELECT count(*)
    FROM non_existant_table t
    WHERE t.color = 'red'
    """
BAD_ERROR = "can not get red count, reason: "
BAD_MESSAGE = (
    "can not get red count, reason: no such table: non_existant_table\n"
    "SELECT count(*)\n"
    "FROM non_existant_table t\n"
    "WHERE t.color = 'red'"
)


@pytest.fixture
def db():
    database = SQLite(DATABASE)
    database.open()
    database.build_database_schema()
    yield database
    database.close()


def test_sql_exception_message_format(db):
    with pytest.raises(DatastoreError) as excinfo:
        parms = []
        db._execute_sql(BAD_SQL, parms, BAD_ERROR)

    assert str(excinfo.value) == BAD_MESSAGE


def test_sql_exception_logs_as_warning(db, caplog):
    with pytest.raises(DatastoreError):
        parms = []
        db._execute_sql(BAD_SQL, parms, BAD_ERROR)

    assert len(caplog.records) == 1
    log_record = caplog.records[0]
    assert log_record.levelname == "WARNING"
    assert log_record.name == "shrikenet.adapters.sqlite"
    assert log_record.message == BAD_MESSAGE
