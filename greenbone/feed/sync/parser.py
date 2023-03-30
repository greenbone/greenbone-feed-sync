# Copyright (C) 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any, Optional, Sequence

from greenbone.feed.sync.__version__ import __version__
from greenbone.feed.sync.config import (
    DEFAULT_CONFIG_FILE,
    DEFAULT_USER_CONFIG_FILE,
    Config,
    maybe_int,
)
from greenbone.feed.sync.errors import ConfigFileError


def _to_defaults(values: dict[str, Any]) -> dict[str, Any]:
    defaults = {}

    for key, value in values.items():
        defaults[key.replace("-", "_")] = value

    return defaults


def feed_type(value: str) -> str:
    """
    Converts to a specific feed type
    """

    value = value.replace("_", "-").lower()

    if value in ("nvts", "report-formats", "port-lists", "scan-configs"):
        return value[:-1]

    return value


class CliParser:
    """
    An ArgumentParser for the feed sync CLI
    """

    def __init__(self) -> None:
        parser = ArgumentParser(add_help=False)
        parser.add_argument(
            "--version",
            help="Print version then exit.",
            action="version",
            version=f"%(prog)s {__version__}",
        )
        parser.add_argument(
            "-h",
            "--help",
            help="Show this help message and exit.",
            action="store_true",
        )
        parser.add_argument(
            "--selftest",
            help="Perform self-test and set exit code",
            action="store_true",
        )
        output_group = parser.add_mutually_exclusive_group()
        output_group.add_argument(
            "--verbose",
            "-v",
            action="count",
            help="Set log verbosity. `-vvv` for maximum verbosity. "
            "(Default: %(default)s)",
        )
        output_group.add_argument(
            "--quiet", action="store_true", help="Disable all log output."
        )

        parser.add_argument(
            "-c",
            "--config",
            help="Configuration file path. If not set %(prog)s "
            f"tries to load {DEFAULT_USER_CONFIG_FILE} or "
            f"{DEFAULT_CONFIG_FILE}.",
        )
        parser.add_argument(
            "--private-directory",
            help="(Sub-)Directory to exclude from the sync which will never "
            "get deleted automatically.",
            type=Path,
        )
        parser.add_argument(
            "--compression-level",
            type=int,
            choices=range(0, 10),
            help="Rsync compression level (0-9). (Default: %(default)s)",
        )
        parser.add_argument(
            "--type",
            choices=[
                "all",
                "nvt",
                "gvmd-data",
                "scap",
                "cert",
                "notus",
                "nasl",
                "report-format",
                "scan-config",
                "port-list",
            ],
            default="all",
            type=feed_type,
            help="Select which feed should be synced. (Default: %(default)s)",
        )
        parser.add_argument(
            "--gvmd-data-destination",
            type=Path,
            help="Destination of the downloaded gvmd data. "
            "(Default: %(default)s)",
        )
        parser.add_argument(
            "--gvmd-data-url",
            help="URL to download the gvmd data from. "
            "(Default: %(default)s)",
        )
        nvts_destination_group = parser.add_argument_group()
        nvts_destination_group.add_argument(
            "--notus-destination",
            type=Path,
            help="Destination of the downloaded notus data. "
            "(Default: %(default)s)",
        )
        nvts_url_group = parser.add_argument_group()
        nvts_url_group.add_argument(
            "--notus-url",
            help="URL to download the notus data from. "
            "(Default: %(default)s)",
        )
        nvts_destination_group.add_argument(
            "--nasl-destination",
            type=Path,
            help="Destination of the downloaded nasl data. "
            "(Default: %(default)s)",
        )
        nvts_url_group.add_argument(
            "--nasl-url",
            help="URL to download the nasl data from. "
            "(Default: %(default)s)",
        )

        secinfo_destination_group = parser.add_argument_group()
        secinfo_destination_group.add_argument(
            "--scap-data-destination",
            type=Path,
            help="Destination of the downloaded SCAP data. "
            "(Default: %(default)s)",
        )
        secinfo_url_group = parser.add_argument_group()
        secinfo_url_group.add_argument(
            "--scap-data-url",
            help="URL to download the SCAP data from. "
            "(Default: %(default)s)",
        )
        secinfo_destination_group.add_argument(
            "--cert-data-destination",
            type=Path,
            help="Destination of the downloaded CERT data. "
            "(Default: %(default)s)",
        )
        secinfo_url_group.add_argument(
            "--cert-data-url",
            help="URL to download the CERT data from. "
            "(Default: %(default)s)",
        )

        data_objects_destination_group = parser.add_argument_group()
        data_objects_destination_group.add_argument(
            "--report-formats-destination",
            type=Path,
            help="Destination of the downloaded report format data "
            "(Default: %(default)s)",
        )
        data_objects_url_group = parser.add_argument_group()
        data_objects_url_group.add_argument(
            "--report-formats-url",
            help="URL to download the report format data from. "
            "(Default: %(default)s)",
        )
        data_objects_destination_group.add_argument(
            "--scan-configs-destination",
            type=Path,
            help="Destination of the downloaded scan config data. "
            "(Default: %(default)s)",
        )
        data_objects_url_group.add_argument(
            "--scan-configs-url",
            help="URL to download the scan config data from. "
            "(Default: %(default)s)",
        )
        data_objects_destination_group.add_argument(
            "--port-lists-destination",
            type=Path,
            help="Destination of the downloaded port list data. "
            "(Default: %(default)s)",
        )
        data_objects_url_group.add_argument(
            "--port-lists-url",
            help="URL to download the port list data from. "
            "(Default: %(default)s)",
        )

        lock_file_group = parser.add_argument_group()
        lock_file_group.add_argument(
            "--gvmd-lock-file",
            type=Path,
            help="File to use for locking the feed synchronization for data "
            "loaded by the gvmd daemon. Used to avoid that more then one "
            "process accesses the feed data at the same time. "
            "(Default: %(default)s)",
        )
        lock_file_group.add_argument(
            "--openvas-lock-file",
            type=Path,
            help="File to use for locking the feed synchronization for data "
            "loaded by the openvas scanner. Used to avoid that more then one "
            "process accesses the feed data at the same time. "
            "(Default: %(default)s)",
        )
        parser.add_argument(
            "--fail-fast",
            "--failfast",
            action="store_true",
            help="Stop after a first error has occurred. Otherwise the script "
            "tries to download additional data if specified.",
        )

        wait_group = parser.add_mutually_exclusive_group()
        wait_group.add_argument(
            "--no-wait",
            action="store_true",
            help="Fail directly if the lock file can't be acquired.",
        )
        wait_group.add_argument(
            "--wait-interval",
            type=int,
            help="Time to wait in seconds after failed lock attempt before"
            "re-trying to lock the file. (Default: %(default)s seconds)",
        )

        parser.add_argument(
            "--rsync-timeout",
            type=int,
            help="Maximum I/O timeout in seconds used for rsync. If no data is "
            "transferred for the specified time then rsync will exit. By "
            "default no timeout is set and the rsync default will be used.",
        )

        permissions_group = parser.add_argument_group()
        permissions_group.add_argument(
            "--user",
            type=maybe_int,
            help="If started as root, use this user name or ID to run the "
            "script. (Default: %(default)s)",
        )
        permissions_group.add_argument(
            "--group",
            type=maybe_int,
            help="If started as root, use this group name or ID to run the "
            "script. (Default: %(default)s)",
        )

        self.parser = parser

    def _load_config(self, config_file: str) -> Config:
        config_path = None

        if config_file is None:
            for file in [DEFAULT_USER_CONFIG_FILE, DEFAULT_CONFIG_FILE]:
                path = Path(file).expanduser().resolve()
                if path.exists():
                    config_path = path
                    break

        else:
            config_path = Path(config_file).expanduser().resolve()
            if not config_path.exists():
                raise ConfigFileError(
                    f"Config file {config_file} does not exist."
                )

        return Config.load(config_path)

    def _set_defaults(self, config_file: Optional[str] = None) -> None:
        config = self._load_config(config_file)
        self.parser.set_defaults(**_to_defaults(config))

    def parse_arguments(
        self, args: Optional[Sequence[str]] = None
    ) -> Namespace:
        """
        Parse CLI arguments
        """
        # Parse args to get the config file path passed as option
        known_args, _ = self.parser.parse_known_args(args)

        # Load the defaults from the config file if it exists.
        # This also override what was passed as cmd option.
        self._set_defaults(known_args.config)

        if known_args.help:
            self.parser.print_help()
            self.parser.exit(0)

        return self.parser.parse_args(args)
