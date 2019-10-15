import pytest

from shrike.adapters.example_crypto_adapter import ExampleCryptoAdapter
from shrike.adapters.memory_adapter import MemoryAdapter
from shrike.entities.app_user import AppUser
from shrike.entities.services import Services
from shrike.usecases.login_to_system import LoginToSystem
from shrike.usecases.login_to_system_input import LoginToSystemInput
from shrike.usecases.login_to_system_output import LoginToSystemOutput

GOOD_USER_USERNAME = 'fmulder'
GOOD_USER_PASSWORD = 'scully'

@pytest.fixture
def services():
    storage_provider = MemoryAdapter()
    storage_provider.open()
    text_transformer = None
    crypto_provider = ExampleCryptoAdapter()
    yield Services(storage_provider, text_transformer, crypto_provider)
    storage_provider.close()

def test_returns_login_output_object(services):
    login_input = LoginToSystemInput('name', 'password', services)
    login_output = LoginToSystem.execute(login_input)
    assert isinstance(login_output, LoginToSystemOutput)

def test_successful_login_output(services):
    username = GOOD_USER_USERNAME
    password = GOOD_USER_PASSWORD
    create_and_store_user(username, password, services)
    login_input = LoginToSystemInput(username, password, services)
    login_output = LoginToSystem.execute(login_input)
    assert login_output.login_successful

def create_and_store_user(username, password, services):
    storage_provider = services.storage_provider
    crypto_provider = services.crypto_provider
    oid = storage_provider.get_next_app_user_oid()
    name = 'mr ' + username
    password_hash = crypto_provider.generate_hash_from_string(password)
    user = AppUser(oid, username, name, password_hash)
    storage_provider.add_app_user(user)
    storage_provider.commit()

def test_wrong_password_login_fail(services):
    username = GOOD_USER_USERNAME
    password = GOOD_USER_PASSWORD
    create_and_store_user(username, password, services)
    password = 'wrong'
    login_input = LoginToSystemInput(username, password, services)
    login_output = LoginToSystem.execute(login_input)
    assert login_output.login_successful is False
    assert login_output.message == 'Login attempt failed.'
