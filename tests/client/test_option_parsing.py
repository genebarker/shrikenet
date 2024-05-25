import configparser
import getpass
import os
import pathlib
import tempfile

import jwt
import pytest

import shrikenet
from shrikenet.client.command_processor import CommandProcessor
from shrikenet.client.flask_adapter import FlaskAdapter


TEST_USER = "fmulder"
TEST_HOSTNAME = "localhost"
TEST_PORT = "5000"
ACCOUNT_NAME = f"{TEST_USER}@{TEST_HOSTNAME}:{TEST_PORT}"
TEST_PASSWORD = "scully"


@pytest.fixture
def config():
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = pathlib.Path(temp_dir) / "testconfig"
        yield config_path


@pytest.fixture
def http(client):
    yield FlaskAdapter(client)


def test_error_code_when_no_command(config):
    exit_code = run_snet(config)
    assert exit_code == 2


def run_snet(config, http=None, args=None):
    processor = CommandProcessor(
        config_path_override=config,
        http_provider_override=http,
    )
    with pytest.raises(SystemExit) as excinfo:
        processor.run(args)
    return excinfo.value.code


def test_usage_info_when_no_command(capsys, config):
    run_snet(config)
    captured = capsys.readouterr()
    assert_has_header(captured.err)
    assert "usage:" in captured.err


def assert_has_header(output):
    assert "snet" in output


def test_error_code_on_unknown_command(config):
    exit_code = run_snet_cmd("bogus", config)
    assert exit_code == 2


def run_snet_cmd(cmd, config, http=None):
    args = cmd if isinstance(cmd, list) else cmd.split()
    return run_snet(config, http=http, args=args)


def test_shows_header_with_error_on_unknown_command(config, capsys):
    run_snet_cmd("bogus", config)
    captured = capsys.readouterr()
    assert_has_header(captured.err)
    assert "invalid choice" in captured.err


@pytest.mark.parametrize(
    ("command"),
    (
        ("license"),
        ("version"),
    ),
)
def test_no_error_code(command, config):
    error_code = run_snet_cmd(command, config)
    assert error_code == 0


def test_license_command_shows_it_with_header(config, capsys):
    run_snet_cmd("license", config)
    captured = capsys.readouterr()
    assert_has_header(captured.out)
    assert "GNU AFFERO" in captured.out


def test_license_shows_regardless_of_run_path(config, capsys):
    homepath = os.environ["HOME"]
    os.chdir(homepath)
    run_snet_cmd("license", config)
    captured = capsys.readouterr()
    assert "GNU AFFERO" in captured.out


def test_version_command_shows_it(config, capsys):
    run_snet_cmd("version", config)
    captured = capsys.readouterr()
    assert f"snet v{shrikenet.__version__}" in captured.out


def test_help_shows_usage_info_with_header(config, capsys):
    run_snet_cmd("-h", config)
    captured = capsys.readouterr()
    assert_has_header(captured.out)
    assert "usage:" in captured.out


def test_open_no_args_shows_error(config, capsys):
    error_code = run_snet_cmd("open", config)
    captured = capsys.readouterr()
    assert error_code == 2
    assert "error" in captured.err


def test_first_open_gets_web_token(monkeypatch, config, http):
    perform_open_with_password(monkeypatch, config, http)
    parser = configparser.ConfigParser()
    parser.read(config)
    token = parser[ACCOUNT_NAME]["token"]
    header = jwt.get_unverified_header(token)
    assert header["typ"] == "JWT"


def perform_open_with_password(monkeypatch, config, http):
    monkeypatch.setattr(getpass, "getpass", good_password)
    return run_snet_cmd(["open", ACCOUNT_NAME], config, http)


def good_password():
    return TEST_PASSWORD


def test_first_open_stores_account_info_in_config(
    monkeypatch, config, http
):
    perform_open_with_password(monkeypatch, config, http)
    parser = configparser.ConfigParser()
    parser.read(config)
    assert ACCOUNT_NAME in parser.sections()
    assert parser[ACCOUNT_NAME]["protocol"] == "http"
    assert parser[ACCOUNT_NAME].getboolean("is_open")
    assert "token" in parser[ACCOUNT_NAME]


def test_first_open_returns_expected_output(
    monkeypatch, config, http, capsys
):
    error_code = perform_open_with_password(monkeypatch, config, http)
    captured = capsys.readouterr()
    assert error_code == 0
    assert f"Opened '{TEST_USER}' at '{TEST_HOSTNAME}'" in captured.out
