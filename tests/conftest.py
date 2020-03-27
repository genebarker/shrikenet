from configparser import ConfigParser

import pytest

from shrike import create_app
from shrike.db import get_services, init_db


@pytest.fixture
def app():
    config = ConfigParser()
    config.read('database.cfg')
    app = create_app({
        'TESTING': True,
        'STORAGE_PROVIDER_MODULE': 'shrike.adapters.postgresql_adapter',
        'STORAGE_PROVIDER_CLASS': 'PostgreSQLAdapter',
        'DB_NAME': config['development']['db_name'],
        'DB_USER': config['development']['db_user'],
        'DB_PASSWORD': config['development']['db_password'],
        'TEXT_TRANSFORMER_MODULE': 'shrike.adapters.markdown',
        'TEST_TRANSFORMER_CLASS': 'Markdown',
        'CRYPTO_PROVIDER_MODULE': 'shrike.adapters.swapcase_adapter',
        'CRYPTO_PROVIDER_CLASS': 'SwapcaseAdapter',
    })

    with app.app_context():
        init_db()
        postgresql_adapter = get_services().storage_provider
        postgresql_adapter._execute_sql_file('pg_load_test_data.sql')
        postgresql_adapter.commit()

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

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)
