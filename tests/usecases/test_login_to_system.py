from datetime import datetime, timedelta, timezone

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
    services.storage_provider.commit()
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


def test_password_fail_count_increments_on_wrong_password(services):
    user_before = create_user_with_two_password_failures(services)
    login_to_system = LoginToSystem(services)
    login_to_system.run(user_before.username, 'wrong_password')
    db = services.storage_provider
    user_after = db.get_app_user_by_username(user_before.username)
    assert user_after.ongoing_password_failure_count == 3


def create_user_with_two_password_failures(services):
    db = services.storage_provider
    user = create_user(services, GOOD_USER_USERNAME, GOOD_USER_PASSWORD)
    user.ongoing_password_failure_count = 2
    two_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=2)
    user.last_password_failure_time = two_minutes_ago
    db.add_app_user(user)
    return user


def test_password_fail_time_set_on_wrong_password(services, good_user):
    login_to_system = LoginToSystem(services)
    time_before_attempt = datetime.now(timezone.utc)
    login_to_system.run(GOOD_USER_USERNAME, 'wrong_password')
    time_after_attempt = datetime.now(timezone.utc)
    db = services.storage_provider
    user_after = db.get_app_user_by_username(GOOD_USER_USERNAME)
    assert user_after.last_password_failure_time > time_before_attempt
    assert user_after.last_password_failure_time < time_after_attempt


def test_user_record_changes_on_wrong_password(services):
    user_before = create_user_with_two_password_failures(services)
    login_to_system = LoginToSystem(services)
    login_to_system.run(user_before.username, 'wrong_password')
    db = services.storage_provider
    db.rollback()
    user_after = db.get_app_user_by_username(user_before.username)
    assert user_after != user_before


def test_user_locks_on_consecutive_password_failures(services, good_user):
    login_to_system = LoginToSystem(services)
    for _ in range(Constants.LOGIN_FAIL_THRESHOLD_COUNT + 1):
        login_to_system.run(GOOD_USER_USERNAME, 'wrong_password')

    db = services.storage_provider
    user = db.get_app_user_by_username(GOOD_USER_USERNAME)
    assert user.is_locked


def test_login_succeeds_for_good_credentials(services, good_user):
    login_to_system = LoginToSystem(services)
    result = login_to_system.run(GOOD_USER_USERNAME, GOOD_USER_PASSWORD)
    validate_successful_result(good_user, result, 'Login successful.')


def validate_successful_result(user, login_result, expected_login_message):
    assert login_result.user_oid == user.oid
    assert not login_result.has_failed
    assert not login_result.must_change_password
    assert login_result.message.startswith(expected_login_message)


def test_password_fail_count_reset_on_successful_login(services):
    user_before = create_user_with_two_password_failures(services)
    login_to_system = LoginToSystem(services)
    login_to_system.run(user_before.username, GOOD_USER_PASSWORD)
    db = services.storage_provider
    db.rollback()
    user_after = db.get_app_user_by_username(user_before.username)
    assert user_after.ongoing_password_failure_count == 0


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
    user = create_needs_password_change_user(services)
    login_to_system = LoginToSystem(services)
    new_password = reverse_string(GOOD_USER_PASSWORD)
    result = login_to_system.run(GOOD_USER_USERNAME, GOOD_USER_PASSWORD,
                                 new_password)
    validate_successful_password_change_result(user, result)


def validate_successful_password_change_result(user, result):
    validate_successful_result(user, result, 'Login successful. Password '
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
    validate_successful_password_change_result(good_user, result)


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


def test_lock_checked_before_password(services):
    create_locked_user(services)
    validate_login_fails(services, GOOD_USER_USERNAME, 'wrong_password',
                         message='Login attempt failed. Your account is '
                                 'locked.')


def test_login_fails_when_user_dormant(services):
    create_dormant_user(services)
    validate_login_fails(services, GOOD_USER_USERNAME, GOOD_USER_PASSWORD,
                         message='Login attempt failed. Your credentials '
                                 'are invalid.')


def create_dormant_user(services):
    user = create_user(services, GOOD_USER_USERNAME, GOOD_USER_PASSWORD)
    user.is_dormant = True
    services.storage_provider.add_app_user(user)
    return user


def test_dormant_checked_before_password(services):
    create_dormant_user(services)
    validate_login_fails(services, GOOD_USER_USERNAME, 'wrong_password',
                         message='Login attempt failed. Your credentials '
                                 'are invalid.')
