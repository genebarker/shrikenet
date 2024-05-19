import pytest

from shrikenet import create_app
from shrikenet.db import get_services, init_db


DATABASE_FILE = "test.db"
DATABASE_DATA = "load_test_data.sql"


@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "STORAGE_PROVIDER_MODULE": "shrikenet.adapters.sqlite",
            "STORAGE_PROVIDER_CLASS": "SQLiteAdapter",
            "STORAGE_PROVIDER_DB": DATABASE_FILE,
            "TEXT_TRANSFORMER_MODULE": "shrikenet.adapters.markdown",
            "TEST_TRANSFORMER_CLASS": "MarkdownAdapter",
            "CRYPTO_PROVIDER_MODULE": "shrikenet.adapters.swapcase",
            "CRYPTO_PROVIDER_CLASS": "SwapcaseAdapter",
            "PASSWORD_CHECKER_MODULE": "shrikenet.adapters.zxcvbn",
            "PASSWORD_CHECKER_CLASS": "zxcvbnAdapter",
            "PASSWORD_MIN_STRENGTH": 2,
            "LOGGING_FORMAT": "%(asctime)s %(levelname)s %(name)s -> %(message)s",
            "LOGGING_DATE_FORMAT": "%Y-%m-%d %H:%M:%S",
            "LOGGING_LEVEL": "DEBUG",
            "LOGGING_FILE": None,
        }
    )

    with app.app_context():
        init_db()
        db = get_services().storage_provider
        db._execute_sql_file(DATABASE_DATA)
        db.commit()

    yield app

    pass


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username="test", password="test"):
        return self._client.post(
            "/auth/login", data={"username": username, "password": password}
        )

    def logout(self):
        return self._client.get("/auth/logout")


@pytest.fixture
def auth(client):
    return AuthActions(client)
