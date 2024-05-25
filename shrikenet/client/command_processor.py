from argparse import ArgumentParser
from configparser import ConfigParser
from pathlib import Path
import getpass
import os
import sys
import textwrap

import shrikenet
from shrikenet.client.requests_adapter import RequestsAdapter

COMMAND_NAME = "snet"
PROJECT_URL = "https://github.com/genebarker/shrikenet"
DEFAULT_CONFIG_FILENAME = ".snetrc"


class CommandProcessor:

    def __init__(
        self, config_path_override=None, http_provider_override=None
    ):
        self.config_path_override = config_path_override
        self.http_provider_override = http_provider_override

    def run(self, arg_list=None):
        parser = self.build_parser()
        args = parser.parse_args(arg_list)
        args.func(args)

    def build_parser(self):
        parser = ArgumentParser(
            prog=COMMAND_NAME,
            description=f"{COMMAND_NAME} is the command line client for shrikenet",
            epilog=f"shrikenet home page: <{PROJECT_URL}>",
        )
        sub_parsers = parser.add_subparsers(
            required=True,
        )
        open_parser = sub_parsers.add_parser(
            "open",
            help="open connection to server",
        )
        open_parser.add_argument(
            "-p",
            "--port",
            type=int,
            help="use custom port",
        )
        open_parser.add_argument(
            "-u",
            "--http",
            action="store_true",
            help="use HTTP protocol (default is HTTPS)",
        )
        open_parser.add_argument(
            "address",
            help="user's shrikenet address (i.e. me@example.com)",
        )
        open_parser.set_defaults(func=self.open_cmd)
        license_parser = sub_parsers.add_parser(
            "license",
            help="show license",
        )
        license_parser.set_defaults(func=self.license_cmd)
        version_parser = sub_parsers.add_parser(
            "version",
            help="show version info",
        )
        version_parser.set_defaults(func=self.version_cmd)
        return parser

    def print_header(self):
        version = shrikenet.__version__
        text = textwrap.dedent(
            f"""\
            {COMMAND_NAME} v{version} - The command line client for shrikenet.
            Copyright (C) 2024 shrikenet project.
            This program comes with ABSOLUTELY NO WARRANTY. This is free software.
            Type '{COMMAND_NAME} license' for details.
            """
        )
        print(text)

    def eprint(self, *args, **kwargs):
        print(*args, file=sys.stderr, **kwargs)

    def license_cmd(self, arg_list=None):
        self.print_header()
        license_filepath = self.get_license_filepath()
        with open(license_filepath) as text_file:
            print(text_file.read())
        sys.exit(0)

    def get_license_filepath(self):
        this_path = os.path.dirname(__file__)
        return os.path.join(this_path, "../../LICENSE.md")

    def version_cmd(self, arg_list=None):
        version = shrikenet.__version__
        print(f"{COMMAND_NAME} v{version}")
        sys.exit(0)

    def open_cmd(self, args):
        if args.address is None:
            self.eprint(
                "ERROR: A target account ID (i.e. me@example.com) must "
                "be provided."
            )
            sys.exit(1)

        account_name = args.address
        protocol = "http"

        username = self.get_username(account_name)
        host_url = f"{protocol}://{self.get_host(account_name)}"
        password = getpass.getpass()

        http = self.get_http_provider(host_url)
        response = http.post(
            "/api/get_token",
            json={
                "username": username,
                "password": password,
            },
        )
        token = response.json["token"]
        expire_time = response.json["expire_time"]
        self.update_config_file_for_open(
            account_name, protocol, token, expire_time
        )
        self.print_open_successful(account_name)
        sys.exit(0)

    def get_host(self, account_name):
        chunk = account_name.split("@")
        return chunk[1]

    def get_http_provider(self, host_url):
        if self.http_provider_override is not None:
            return self.http_provider_override
        return RequestsAdapter(host_url)

    def update_config_file_for_open(
        self,
        account_name,
        protocol,
        token,
        expire_time,
    ):
        config = ConfigParser()
        config[account_name] = {}
        config[account_name]["protocol"] = protocol
        config[account_name]["is_open"] = "true"
        config[account_name]["token"] = token
        config[account_name]["expire_time"] = expire_time
        config_path = self.get_config_path()
        with open(config_path, "w") as configfile:
            config.write(configfile)

    def get_config_path(self):
        if self.config_path_override is not None:
            return self.config_path_override

        config_path = Path.home() / DEFAULT_CONFIG_FILENAME
        return config_path

    def print_open_successful(self, account_name):
        username = self.get_username(account_name)
        hostname = self.get_hostname(account_name)
        print(f"Opened '{username}' at '{hostname}'")

    def get_username(self, account_name):
        chunk = account_name.split("@")
        return chunk[0]

    def get_hostname(self, account_name):
        chunk_one = account_name.split("@")
        chunk_two = chunk_one[1].split(":")
        return chunk_two[0]
