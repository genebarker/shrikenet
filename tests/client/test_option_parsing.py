import configparser
import os
import pathlib
import tempfile

import pytest

import shrikenet
from shrikenet.client.command_processor import CommandProcessor


TEST_USER = 'fmulder'
TEST_HOSTNAME = 'localhost'
TEST_PORT = '5000'
ACCOUNT_NAME = f'{TEST_USER}@{TEST_HOSTNAME}:{TEST_PORT}'


@pytest.fixture
def config():
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = pathlib.Path(temp_dir) / 'testconfig'
        yield config_path


def test_error_code_when_no_command(config):
    exit_code = run_snet(config)
    assert exit_code == 1


def run_snet(config, args=None):
    processor = CommandProcessor(config_path_override=config)
    with pytest.raises(SystemExit) as excinfo:
        processor.run(args)
    return excinfo.value.code


def test_usage_info_when_no_command(capsys, config):
    run_snet(config)
    captured = capsys.readouterr()
    assert_has_header(captured.out)
    assert 'Usage:' in captured.out


def assert_has_header(output):
    assert 'snet' in output


def test_error_code_on_unknown_command(config):
    exit_code = run_snet_cmd('bogus', config)
    assert exit_code == 1


def run_snet_cmd(cmd, config):
    args = ['snet', cmd] if isinstance(cmd, str) else ['snet'] + cmd
    return run_snet(config, args)


def test_shows_header_with_error_on_unknown_command(config, capsys):
    run_snet_cmd('bogus', config)
    captured = capsys.readouterr()
    assert_has_header(captured.out)
    assert (
        "ERROR: Unknown command (bogus) provided. Type 'snet help' for help."
        in captured.err
    )


@pytest.mark.parametrize(('command'), (
    ('license'),
    ('version'),
    ('help'),
))
def test_no_error_code(command, config):
    error_code = run_snet_cmd(command, config)
    assert error_code == 0


def test_license_command_shows_it_with_header(config, capsys):
    run_snet_cmd('license', config)
    captured = capsys.readouterr()
    assert_has_header(captured.out)
    assert 'GNU AFFERO' in captured.out


def test_license_shows_regardless_of_run_path(config, capsys):
    homepath = os.environ['HOME']
    os.chdir(homepath)
    run_snet_cmd('license', config)
    captured = capsys.readouterr()
    assert 'GNU AFFERO' in captured.out


def test_version_command_shows_it(config, capsys):
    run_snet_cmd('version', config)
    captured = capsys.readouterr()
    assert f'snet v{shrikenet.__version__}' in captured.out


def test_help_shows_usage_info_with_header(config, capsys):
    run_snet_cmd('help', config)
    captured = capsys.readouterr()
    assert_has_header(captured.out)
    assert 'Usage:' in captured.out


def test_open_no_args_shows_error(config, capsys):
    error_code = run_snet_cmd('open', config)
    captured = capsys.readouterr()
    assert error_code == 1
    assert (
        'ERROR: A target account ID (i.e. me@example.com) must be provided.'
        in captured.err
    )


def test_good_open_stores_account_info_in_config(config):
    run_snet_cmd(['open', ACCOUNT_NAME], config)
    parser = configparser.ConfigParser()
    parser.read(config)
    assert ACCOUNT_NAME in parser.sections()
    assert parser[ACCOUNT_NAME].getboolean('is_open')
    assert 'token' in parser[ACCOUNT_NAME]


def test_good_open_returns_expected_output(config, capsys):
    error_code = run_snet_cmd(['open', ACCOUNT_NAME], config)
    captured = capsys.readouterr()
    assert error_code == 0
    assert f"Opened '{TEST_USER}' at '{TEST_HOSTNAME}'" in captured.out
