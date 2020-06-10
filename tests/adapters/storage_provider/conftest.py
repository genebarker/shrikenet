from configparser import ConfigParser
import importlib

import pytest


memory_adapter = [
    'shrikenet.adapters.memory',
    'Memory',
    None,
]


def get_postgresql_config():
    config = ConfigParser()
    config.read('tests/database.cfg')
    db_config = {
        'db_name': config['development']['db_name'],
        'db_user': config['development']['db_user'],
        'db_password': config['development']['db_password'],
        'db_port': config['development']['db_port'],
    }
    return db_config


postgresql_adapter = [
    'shrikenet.adapters.postgresql',
    'PostgreSQL',
    get_postgresql_config(),
]


# pylint: disable=redefined-outer-name
@pytest.fixture(scope='module', params=[memory_adapter, postgresql_adapter])
def fresh_db(request):
    module = importlib.import_module(request.param[0])
    class_ = getattr(module, request.param[1])
    database = class_(request.param[2])
    database.open()
    database.build_database_schema()
    database.commit()
    yield database
    database.close()


@pytest.fixture
def db(fresh_db):
    database = fresh_db
    database.reset_database_objects()
    database.commit()
    yield database
    database.rollback()


@pytest.fixture(params=[memory_adapter, postgresql_adapter])
def unopened_db(request):
    module = importlib.import_module(request.param[0])
    class_ = getattr(module, request.param[1])
    return class_(request.param[2])
