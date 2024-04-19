from datetime import datetime, timedelta, timezone
import logging

import jwt

from shrikenet.api import token_authority


logging.basicConfig(level=logging.INFO)

TEST_USER_OID = 1
TEST_USER_USERNAME = "test"
TEST_USER_PASSWORD = "test"


def test_get_token_returns_expected_fields(client):
    json_data = do_get_token_with_good_credentials(client)
    assert json_data["error_code"] == 0
    assert json_data["message"] == "Login successful."
    verify_is_jwt_token(json_data["token"])


def do_get_token_with_good_credentials(client):
    response = client.post(
        "/api/get_token",
        json={
            "username": TEST_USER_USERNAME,
            "password": TEST_USER_PASSWORD,
        },
    )
    return response.get_json()


def verify_is_jwt_token(token):
    header = jwt.get_unverified_header(token)
    assert header["typ"] == "JWT"


def test_token_contains_expected_payload(app, client):
    with app.app_context():
        secret_key = app.config["SECRET_KEY"]
        lifespan_days = app.config["TOKEN_LIFESPAN_DAYS"]
    expected_expire_time = datetime.now(timezone.utc) + timedelta(
        days=lifespan_days
    )
    json_data = do_get_token_with_good_credentials(client)
    token = json_data["token"]
    payload = token_authority.decode_token(token, secret_key)
    assert payload["user_oid"] == TEST_USER_OID
    expire_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    assert get_time_str(expire_time) == get_time_str(expected_expire_time)


def get_time_str(time):
    return time.strftime("%Y-%m-%d %H:%M")


def test_get_token_fails_on_bad_credentials(client):
    response = do_get_token_with_bad_credentials(client)
    verify_error(response, 2, "Login attempt failed.")


def do_get_token_with_bad_credentials(client):
    return client.post(
        "/api/get_token",
        json={
            "username": TEST_USER_USERNAME,
            "password": "wrong_password",
        },
    )


def verify_error(response, error_code, message):
    json_data = response.get_json()
    assert json_data["error_code"] == error_code
    assert json_data["message"] == message


def test_token_required_fails_on_bad_token(client):
    response = do_token_required_with_bad_token(client)
    verify_error(
        response, 3, "The provided authorization token is invalid."
    )


def do_token_required_with_bad_token(client):
    return client.post(
        "/api/verify_token",
        headers={"TOKEN": "bad_token"},
        environ_base={"REMOTE_ADDR": "4.3.2.1"},
    )


def test_token_required_logs_on_bad_token(client, caplog):
    do_token_required_with_bad_token(client)
    expected_message = (
        "Method access denied from 4.3.2.1 due to an invalid token "
        "(error_code=3, method=verify_token). Reason: "
    )
    verify_error_logged(caplog, expected_message)


def verify_error_logged(caplog, message, prev_log_count=0):
    for log_record in caplog.records:
        if prev_log_count > 0:
            prev_log_count -= 1
            continue
        assert log_record.levelname == "INFO"
        assert log_record.name == "shrikenet.api.token_authority"
        assert log_record.message.startswith(message)


def test_token_required_fails_on_none(client):
    response = client.post("/api/verify_token")
    verify_error(response, 1, "An authorization token is required.")


def test_token_required_logs_on_none(client, caplog):
    client.post(
        "/api/verify_token",
        environ_base={"REMOTE_ADDR": "4.5.6.7"},
    )
    verify_error_logged(
        caplog,
        "Method access denied from 4.5.6.7 since no token provided "
        "(error_code=1, method=verify_token).",
    )


def test_token_required_fails_when_expired(app, client):
    response = do_token_required_with_expired_token(app, client)
    verify_error(response, 4, "The authorization token has expired.")


def do_token_required_with_expired_token(app, client):
    with app.app_context():
        secret_key = app.config["SECRET_KEY"]
    user_oid = TEST_USER_OID
    expire_time = datetime.now(timezone.utc) - timedelta(seconds=1)
    expired_token = token_authority.create_token(
        user_oid,
        expire_time,
        secret_key,
    )
    return client.post(
        "/api/verify_token",
        headers={"TOKEN": expired_token},
        environ_base={"REMOTE_ADDR": "9.9.2.2"},
    )


def test_token_required_logs_when_expired(app, client, caplog):
    do_token_required_with_expired_token(app, client)
    verify_error_logged(
        caplog,
        "Method access denied from 9.9.2.2 since the token has expired "
        "(error_code=4, method=verify_token, expire_time=",
    )


def test_token_required_fails_on_exception(app, client):
    response = do_token_required_with_exception(app, client)
    verify_error(
        response,
        5,
        "An unexpected error occurred when processing the authorization "
        "token.",
    )


def do_token_required_with_exception(app, client):
    with app.app_context():
        secret_key = app.config["SECRET_KEY"]
    user_oid = -999
    expire_time = datetime.now(timezone.utc) + timedelta(minutes=1)
    token_with_bad_user = token_authority.create_token(
        user_oid,
        expire_time,
        secret_key,
    )
    return client.post(
        "/api/verify_token",
        headers={"TOKEN": token_with_bad_user},
        environ_base={"REMOTE_ADDR": "10.9.8.7"},
    )


def test_token_required_logs_on_exception(app, client, caplog):
    do_token_required_with_exception(app, client)
    verify_error_logged(
        caplog,
        "Method access denied from 10.9.8.7 since an unexpected error "
        "occurred while processing the token (error_code=5, "
        "method=verify_token). Reason: ",
        prev_log_count=1,
    )
