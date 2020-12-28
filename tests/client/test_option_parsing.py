import os

import pytest

import shrikenet
from shrikenet.client import snet


def test_error_code_when_no_command():
    exit_code = run_snet()
    assert exit_code == 1


def run_snet(args=None):
    with pytest.raises(SystemExit) as excinfo:
        snet.main(args)
    return excinfo.value.code


def test_usage_info_when_no_command(capsys):
    run_snet()
    captured = capsys.readouterr()
    assert_has_header(captured.out)
    assert 'Usage:' in captured.out


def assert_has_header(output):
    assert 'snet' in output


def test_error_code_on_unknown_command():
    args = ['snet', 'bogus']
    exit_code = run_snet(args)
    assert exit_code == 1


def test_shows_header_with_error_on_unknown_command(capsys):
    args = ['snet', 'bogus']
    run_snet(args)
    captured = capsys.readouterr()
    assert_has_header(captured.out)
    assert 'ERROR: unknown command (bogus)' in captured.out


@pytest.mark.parametrize(('command'), (
    ('license'),
    ('version'),
    ('help'),
))
def test_no_error_code(command):
    args = ['snet', command]
    error_code = run_snet(args)
    assert error_code == 0


def test_license_command_shows_it(capsys):
    args = ['snet', 'license']
    run_snet(args)
    captured = capsys.readouterr()
    assert_has_header(captured.out)
    assert 'GNU AFFERO' in captured.out


def test_license_shows_regardless_of_run_path(capsys):
    homepath = os.environ['HOME']
    os.chdir(homepath)
    args = ['snet', 'license']
    run_snet(args)
    captured = capsys.readouterr()
    assert 'GNU AFFERO' in captured.out


def test_version_command_shows_it(capsys):
    args = ['snet', 'version']
    run_snet(args)
    captured = capsys.readouterr()
    assert f'snet v{shrikenet.__version__}' in captured.out


def test_help_shows_usage_info(capsys):
    args = ['snet', 'help']
    run_snet(args)
    captured = capsys.readouterr()
    assert 'Usage:' in captured.out
