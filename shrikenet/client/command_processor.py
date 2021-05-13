from configparser import ConfigParser
from pathlib import Path
import os
import sys
import textwrap

import shrikenet


COMMAND_NAME = 'snet'
DEFAULT_CONFIG_FILENAME = '.snetrc'


class CommandProcessor:

    def __init__(self, config_path_override=None):
        self.config_path_override = config_path_override

    def run(self, arg_list=None):
        if arg_list and len(arg_list) > 1:
            command = arg_list[1]
            command_arg_list = arg_list[2:]
            try:
                func = getattr(self, f'{command}_cmd')
                func(command_arg_list)
            except AttributeError:
                self.print_header()
                self.eprint(
                    f"ERROR: Unknown command ({command}) provided. Type '"
                    f"{COMMAND_NAME} help' for help."
                )
                sys.exit(1)

        self.help_cmd(exit_code=1)

    def print_header(self):
        version = shrikenet.__version__
        text = textwrap.dedent(f"""\
            {COMMAND_NAME} v{version} - The command line client for shrikenet.
            Copyright (C) 2021 Eugene F. Barker. Web: https://github.com/genebarker
            This program comes with ABSOLUTELY NO WARRANTY. This is free software.
            Type '{COMMAND_NAME} license' for details.
            """)
        print(text)

    def eprint(self, *args, **kwargs):
        print(*args, file=sys.stderr, **kwargs)

    def help_cmd(self, arg_list=None, exit_code=0):
        self.print_header()
        self.print_usage()
        sys.exit(exit_code)

    def print_usage(self):
        text = textwrap.dedent(f"""\
            Usage:
              {COMMAND_NAME} status
              {COMMAND_NAME} open [user@host[:port]]
              {COMMAND_NAME} close [user@host]
              {COMMAND_NAME} license
              {COMMAND_NAME} version
              {COMMAND_NAME} help [command]
            """)
        print(text)

    def license_cmd(self, arg_list=None):
        self.print_header()
        license_filepath = self.get_license_filepath()
        with open(license_filepath) as text_file:
            print(text_file.read())
        sys.exit(0)

    def get_license_filepath(self):
        this_path = os.path.dirname(__file__)
        return os.path.join(this_path, '../../LICENSE.md')

    def version_cmd(self, arg_list=None):
        version = shrikenet.__version__
        print(f'{COMMAND_NAME} v{version}')
        sys.exit(0)

    def open_cmd(self, arg_list=None):
        if arg_list is None or len(arg_list) == 0:
            self.eprint(
                'ERROR: A target account ID (i.e. me@example.com) must '
                'be provided.'
            )
            sys.exit(1)

        account_name = arg_list[0]
        self.update_config_file_for_open(account_name)
        self.print_open_successful(account_name)
        sys.exit(0)

    def update_config_file_for_open(self, account_name):
        config = ConfigParser()
        config[account_name] = {}
        config[account_name]['is_open'] = 'true'
        config[account_name]['token'] = 'fake_token'
        config_path = self.get_config_path()
        with open(config_path, 'w') as configfile:
            config.write(configfile)

    def get_config_path(self):
        if self.config_path_override is not None:
            return self.config_path_override
        return Path(DEFAULT_CONFIG_FILENAME)

    def print_open_successful(self, account_name):
        username = self.get_username(account_name)
        hostname = self.get_hostname(account_name)
        print(f"Opened '{username}' at '{hostname}'")

    def get_username(self, account_name):
        chunk = account_name.split('@')
        return chunk[0]

    def get_hostname(self, account_name):
        chunk_one = account_name.split('@')
        chunk_two = chunk_one[1].split(':')
        return chunk_two[0]
