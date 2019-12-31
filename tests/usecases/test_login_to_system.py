import pytest

from shrike.adapters.memory_adapter import MemoryAdapter
from shrike.adapters.swapcase_adapter import SwapcaseAdapter
from shrike.entities.app_user import AppUser
from shrike.entities.constants import Constants
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
    user = create_user(services, GOOD_USER_USERNAME, GOOD_USER_PASSWORD)
    services.storage_provider.add_app_user(user)
    return user


def create_user(services, username, password):
    oid = services.storage_provider.get_next_app_user_oid()
    name = 'mr ' + username
    password_hash = services.crypto_provider.generate_hash_from_string(
        password)
    user = AppUser(oid, username, name, password_hash)
    return user


def test_login_fails_on_unknown_username(services):
    validate_login_fails(services, 'unknown_username', 'some password')


def validate_login_fails(services, username, password,
                         message='Login attempt failed.'):
    login_to_system = LoginToSystem(services)
    result = login_to_system.run(username, password)
    assert result.has_failed
    assert not result.must_change_password
    assert result.message == message


def test_login_fails_on_wrong_password(services, good_user):
    validate_login_fails(services, GOOD_USER_USERNAME, 'wrong_password')


def test_login_succeeds_for_good_credentials(services, good_user):
    login_to_system = LoginToSystem(services)
    result = login_to_system.run(GOOD_USER_USERNAME, GOOD_USER_PASSWORD)
    validate_successful_result(result, 'Login successful.')


def validate_successful_result(login_result, expected_login_message):
    assert not login_result.has_failed
    assert not login_result.must_change_password
    assert login_result.message.startswith(expected_login_message)


def test_login_fails_when_password_marked_for_reset(services):
    create_needs_password_change_user(services)
    login_to_system = LoginToSystem(services)
    result = login_to_system.run(GOOD_USER_USERNAME, GOOD_USER_PASSWORD)
    assert result.has_failed
    assert result.must_change_password
    assert result.message == ('Password marked for reset. Must supply a '
                              'new password.')


def create_needs_password_change_user(services):
    user = create_user(services, GOOD_USER_USERNAME, GOOD_USER_PASSWORD)
    user.needs_password_change = True
    services.storage_provider.add_app_user(user)
    return user


def test_login_succeeds_when_password_marked_for_reset_and_new_provided(
        services):
    create_needs_password_change_user(services)
    login_to_system = LoginToSystem(services)
    new_password = reverse_string(GOOD_USER_PASSWORD)
    result = login_to_system.run(GOOD_USER_USERNAME, GOOD_USER_PASSWORD,
                                 new_password)
    validate_successful_password_change_result(result)


def validate_successful_password_change_result(result):
    validate_successful_result(result, 'Login successful. Password '
                                       'successfully changed')


def test_credentials_checked_before_password_reset(services):
    user = create_user(services, GOOD_USER_USERNAME, GOOD_USER_PASSWORD)
    user.needs_password_change = True
    services.storage_provider.add_app_user(user)
    validate_login_fails(services, GOOD_USER_USERNAME, 'wrong_password')


def test_login_with_new_password_returns_successful_result(services,
                                                           good_user):
    login_to_system = LoginToSystem(services)
    new_password = reverse_string(GOOD_USER_PASSWORD)
    result = login_to_system.run(GOOD_USER_USERNAME, GOOD_USER_PASSWORD,
                                 new_password)
    validate_successful_password_change_result(result)


def reverse_string(string):
    return string[::-1]


def test_login_with_new_password_changes_the_password(services, good_user):
    login_to_system = LoginToSystem(services)
    new_password = reverse_string(GOOD_USER_PASSWORD)
    login_to_system.run(GOOD_USER_USERNAME, GOOD_USER_PASSWORD,
                        new_password)
    services.storage_provider.rollback()
    user = services.storage_provider.get_app_user_by_oid(good_user.oid)
    assert services.crypto_provider.hash_matches_string(user.password_hash,
                                                        new_password)


def test_login_fails_when_user_locked(services):
    create_locked_user(services)
    validate_login_fails(services, GOOD_USER_USERNAME, GOOD_USER_PASSWORD,
                         message='Login attempt failed. Your account is '
                                 'locked.')


def create_locked_user(services):
    user = create_user(services, GOOD_USER_USERNAME, GOOD_USER_PASSWORD)
    user.is_locked = True
    services.storage_provider.add_app_user(user)
    return user


def test_password_checked_before_user_lock(services):
    create_locked_user(services)
    validate_login_fails(services, GOOD_USER_USERNAME, 'wrong_password')

# def test_account_locks_on_consecutive_failures(services, good_user):
#     login_to_system = LoginToSystem(services)
#     result = None
#     for _ in range(Constants.LOGIN_FAIL_THRESHOLD_COUNT):
#         result = login_to_system.run(GOOD_USER_USERNAME, 'wrong_password')
#     user = services.storage_provider.get_app_user_by_username(
#         GOOD_USER_USERNAME)
#     assert user.is_locked
#     assert result.has_failed
#     assert result.message == 'Login attempt failed. This account is locked.'
