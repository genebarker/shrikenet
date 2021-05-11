from configparser import ConfigParser
import os
import sys
import textwrap

import shrikenet


def main(arg_list=None):
    if arg_list and len(arg_list) > 1:
        command = arg_list[1]
        command_arg_list = arg_list[2:]
        try:
            func = getattr(sys.modules[__name__], f'{command}_cmd')
            func(command_arg_list)
        except AttributeError:
            print_header()
            eprint(
                f"ERROR: Unknown command ({command}) provided. Type 'snet "
                "help' for help."
            )
            sys.exit(1)

    help_cmd(exit_code=1)


def print_header():
    version = shrikenet.__version__
    text = textwrap.dedent(f"""\
        snet v{version} - The command line client for shrikenet.
        Copyright (C) 2021 Eugene F. Barker. Web: https://github.com/genebarker
        This program comes with ABSOLUTELY NO WARRANTY. This is free software.
        Type 'snet license' for details.
        """)
    print(text)


def help_cmd(arg_list=None, exit_code=0):
    print_header()
    print_usage()
    sys.exit(exit_code)


def print_usage():
    text = textwrap.dedent("""\
        Usage:
          snet status
          snet open [user@host[:port]]
          snet close [user@host]
          snet license
          snet version
          snet help [command]
        """)
    print(text)


def license_cmd(arg_list=None):
    print_header()
    license_filepath = get_license_filepath()
    with open(license_filepath) as text_file:
        print(text_file.read())
    sys.exit(0)


def get_license_filepath(arg_list=None):
    this_path = os.path.dirname(__file__)
    return os.path.join(this_path, '../../LICENSE.md')


def version_cmd(arg_list=None):
    version = shrikenet.__version__
    print(f'snet v{version}')
    sys.exit(0)


def open_cmd(arg_list=None):
    if arg_list is None or len(arg_list) == 0:
        eprint(
            'ERROR: A target account ID (i.e. me@example.com) must '
            'be provided.'
        )
        sys.exit(1)

    full_account_id = arg_list[0]
    update_config_file_for_open(full_account_id)
    print_open_successful(full_account_id)
    sys.exit(0)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def update_config_file_for_open(full_account_id):
    config = ConfigParser()
    config[full_account_id] = {}
    config[full_account_id]['is_open'] = 'true'
    config[full_account_id]['token'] = 'fake_token'
    with open('.snetrc', 'w') as configfile:
        config.write(configfile)


def print_open_successful(full_account_id):
    username = get_username(full_account_id)
    hostname = get_hostname(full_account_id)
    print(f"Opened '{username}' at '{hostname}'")


def get_username(full_account_id):
    chunk = full_account_id.split('@')
    return chunk[0]


def get_hostname(full_account_id):
    chunk_one = full_account_id.split('@')
    chunk_two = chunk_one[1].split(':')
    return chunk_two[0]
