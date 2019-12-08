import pytest

from shrike.adapters.memory_adapter import MemoryAdapter
from shrike.adapters.swapcase_adapter import SwapcaseAdapter
from shrike.entities.app_user import AppUser
from shrike.entities.services import Services
from shrike.usecases.login_to_system import LoginToSystem
from shrike.usecases.login_to_system_result import LoginToSystemResult

GOOD_USER_USERNAME = 'fmulder'
GOOD_USER_PASSWORD = 'scully'


@pytest.fixture
def services():
    storage_provider = MemoryAdapter()
    storage_provider.open()
    text_transformer = None
    crypto_provider = SwapcaseAdapter()
    yield Services(storage_provider, text_transformer, crypto_provider)
    storage_provider.close()


@pytest.fixture
def good_user(services):
    username = GOOD_USER_USERNAME
    password = GOOD_USER_PASSWORD
    create_and_store_user(username, password, services)


def create_and_store_user(username, password, services):
    storage_provider = services.storage_provider
    crypto_provider = services.crypto_provider
    oid = storage_provider.get_next_app_user_oid()
    name = 'mr ' + username
    password_hash = crypto_provider.generate_hash_from_string(password)
    user = AppUser(oid, username, name, password_hash)
    storage_provider.add_app_user(user)
    storage_provider.commit()


def test_login_fails_on_unknown_username(services):
    validate_login_fails(services, 'unknown_username', 'some password')


def validate_login_fails(services, username, password):
    presenter = SimpleResultPresenter()
    login_to_system = LoginToSystem(services, presenter)
    result = login_to_system.run(username, password)
    assert result.was_successful is False
    assert result.must_change_password is False
    assert result.message == 'Login attempt failed.'
    assert presenter.present_method_called


class SimpleResultPresenter:
    def __init__(self):
        self.present_method_called = False

    def present(self, result):
        self.present_method_called = isinstance(result, LoginToSystemResult)


def test_login_fails_on_wrong_password(services, good_user):
    validate_login_fails(services, GOOD_USER_USERNAME, 'wrong password')


def test_login_succeeds_for_good_credentials(services, good_user):
    presenter = SimpleResultPresenter()
    login_to_system = LoginToSystem(services, presenter)
    result = login_to_system.run(GOOD_USER_USERNAME, GOOD_USER_PASSWORD)
    assert result.was_successful
    assert presenter.present_method_called
