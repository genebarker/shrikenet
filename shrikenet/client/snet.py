import os
import sys
import textwrap

import shrikenet


def main(arg_list=None):
    if arg_list and len(arg_list) > 1:
        command = arg_list[1]
        if command == 'license':
            license_cmd()
        elif command == 'version':
            version_cmd()
        elif command == 'help':
            help_cmd()

    exit_code = 1
    help_cmd(exit_code)


def license_cmd():
    print_header()
    license_filepath = get_license_filepath()
    with open(license_filepath) as text_file:
        print(text_file.read())
    sys.exit(0)


def get_license_filepath():
    this_path = os.path.dirname(__file__)
    return os.path.join(this_path, '../../LICENSE.md')


def print_header():
    version = shrikenet.__version__
    text = textwrap.dedent(f"""\
        snet v{version} - The command line client for shrikenet.
        Copyright (C) 2021 Eugene F. Barker. Web: https://github.com/genebarker
        This program comes with ABSOLUTELY NO WARRANTY. This is free software.
        Type 'snet license' for details.
        """)

    print(text)


def version_cmd():
    print_header()
    sys.exit(0)


def help_cmd(exit_code=0):
    print_header()
    print_usage()
    sys.exit(exit_code)


def print_usage():
    text = textwrap.dedent("""\
        Usage:
          snet status
          snet open [USERNAME@HOST]
          snet close [USERNAME@HOST]
          snet license
          snet version
          snet help [COMMAND]
        """)
    print(text)
