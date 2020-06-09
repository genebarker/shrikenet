import pytest

from shrikenet.adapters.postgresql import PostgreSQL
from shrikenet.entities.exceptions import DatastoreError

MODULE_UNDER_TEST = 'shrikenet.adapters.postgresql'

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


@pytest.fixture
def pg_db(db):
    if isinstance(db, PostgreSQL):
        return db
    pytest.skip()


@pytest.mark.parametrize(('method_name',), (
    ('_execute_select_value',),
    ('_execute_process_sql',),
))
def test_sql_exception_message_format(pg_db, method_name):
    db = pg_db
    sql_method = getattr(db, method_name)
    with pytest.raises(DatastoreError) as excinfo:
        parms = None
        sql_method(BAD_SQL, parms, BAD_ERROR)

    assert str(excinfo.value) == BAD_MESSAGE


@pytest.mark.parametrize(('method_name',), (
    ('_execute_select_value',),
    ('_execute_process_sql',),
))
def test_sql_exception_logs_as_warning(pg_db, caplog, method_name):
    db = pg_db
    sql_method = getattr(db, method_name)
    with pytest.raises(DatastoreError):
        parms = None
        sql_method(BAD_SQL, parms, BAD_ERROR)

    assert len(caplog.records) == 1
    log_record = caplog.records[0]
    assert log_record.levelname == 'WARNING'
    assert log_record.name == MODULE_UNDER_TEST
    assert log_record.message == BAD_MESSAGE
