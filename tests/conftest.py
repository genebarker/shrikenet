from configparser import ConfigParser

import pytest

from shrikenet import create_app
from shrikenet.db import get_services, init_db


@pytest.fixture
def app():
    config = ConfigParser()
    config.read('tests/database.cfg')
    app = create_app({
        'TESTING': True,
        'STORAGE_PROVIDER_MODULE': 'shrikenet.adapters.postgresql',
        'STORAGE_PROVIDER_CLASS': 'PostgreSQL',
        'DB_NAME': config['development']['db_name'],
        'DB_USER': config['development']['db_user'],
        'DB_PASSWORD': config['development']['db_password'],
        'DB_PORT': config['development']['db_port'],
        'TEXT_TRANSFORMER_MODULE': 'shrikenet.adapters.markdown',
        'TEST_TRANSFORMER_CLASS': 'Markdown',
        'CRYPTO_PROVIDER_MODULE': 'shrikenet.adapters.swapcase',
        'CRYPTO_PROVIDER_CLASS': 'Swapcase',
    })

    with app.app_context():
        init_db()
        postgresql = get_services().storage_provider
        postgresql._execute_sql_file('pg_load_test_data.sql')
        postgresql.commit()

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
