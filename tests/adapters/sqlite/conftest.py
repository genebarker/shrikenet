import pytest

from shrikenet.adapters.sqlite import SQLiteAdapter
from shrikenet.entities.app_user import AppUser

DB_CONFIG = {
    "STORAGE_PROVIDER_DB": "test.db",
}


@pytest.fixture
def db_config():
    return DB_CONFIG


@pytest.fixture
def db():
    database = SQLiteAdapter(DB_CONFIG)
    database.open()
    database.build_database_schema()
    yield database
    database.close()


@pytest.fixture
def app_user_obj():
    username = "dstrange"
    name = "Dr. Strange"
    password_hash = "easyHARD"
    app_user = AppUser(
        username,
        name,
        password_hash,
    )
    return app_user


@pytest.fixture
def app_user(db, app_user_obj):
    app_user_obj.oid = db.add_app_user(app_user_obj)
    return app_user_obj
