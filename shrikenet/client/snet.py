import os
import sys
import textwrap

import shrikenet


def main(arg_list=None):
    if arg_list and len(arg_list) > 1:
        command = arg_list[1]
        try:
            func = getattr(sys.modules[__name__], f'{command}_cmd')
            func()
        except AttributeError:
            print_header()
            eprint(
                f"ERROR: Unknown command ({command}) provided. Type 'snet "
                "help' for help."
            )
            sys.exit(1)

    exit_code = 1
    help_cmd(exit_code)


def print_header():
    version = shrikenet.__version__
    text = textwrap.dedent(f"""\
        snet v{version} - The command line client for shrikenet.
        Copyright (C) 2021 Eugene F. Barker. Web: https://github.com/genebarker
        This program comes with ABSOLUTELY NO WARRANTY. This is free software.
        Type 'snet license' for details.
        """)
    print(text)


def help_cmd(exit_code=0):
    print_header()
    print_usage()
    sys.exit(exit_code)


def print_usage():
    text = textwrap.dedent("""\
        Usage:
          snet status
          snet open [username@host]
          snet close [username@host]
          snet license
          snet version
          snet help [command]
        """)
    print(text)


def license_cmd():
    print_header()
    license_filepath = get_license_filepath()
    with open(license_filepath) as text_file:
        print(text_file.read())
    sys.exit(0)


def get_license_filepath():
    this_path = os.path.dirname(__file__)
    return os.path.join(this_path, '../../LICENSE.md')


def version_cmd():
    version = shrikenet.__version__
    print(f'snet v{version}')
    sys.exit(0)


def open_cmd():
    eprint(
        'ERROR: A target account ID (i.e. me@example.com) must be provided.'
    )
    sys.exit(1)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
