# Copyright (C) 2023 Greenbone Networks GmbH
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

import os
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any, Optional, Sequence, Union

from greenbone.feed.sync.__version__ import __version__
from greenbone.feed.sync.errors import ConfigFileError
from greenbone.feed.sync.helper import DEFAULT_FLOCK_WAIT_INTERVAL
from greenbone.feed.sync.rsync import (
    DEFAULT_RSYNC_COMPRESSION_LEVEL,
    DEFAULT_RSYNC_URL,
)

try:
    import tomllib
except ImportError:
    import tomli as tomllib


def maybe_int(value: str) -> Union[int, str]:
    """
    Convert string into int if possible
    """
    try:
        value = int(value)
    except ValueError:
        pass

    return value


DEFAULT_NOTUS_URL_PATH = "/vulnerability-feed/22.04/vt-data/notus/"
DEFAULT_NASL_URL_PATH = "/vulnerability-feed/22.04/vt-data/nasl/"
DEFAULT_SCAP_DATA_URL_PATH = "/vulnerability-feed/22.04/scap-data/"
DEFAULT_CERT_DATA_URL_PATH = "/vulnerability-feed/22.04/cert-data/"
DEFAULT_GVMD_DATA_URL_PATH = "/data-feed/22.04/"
DEFAULT_REPORT_FORMATS_URL_PATH = "/data-feed/22.04/report-formats/"
DEFAULT_SCAN_CONFIGS_URL_PATH = "/data-feed/22.04/scan-configs/"
DEFAULT_PORT_LISTS_URL_PATH = "/data-feed/22.04/port-lists/"

DEFAULT_DESTINATION_PREFIX = "/var/lib/"

DEFAULT_NASL_PATH = "openvas/plugins"
DEFAULT_NOTUS_PATH = "notus"
DEFAULT_SCAP_DATA_PATH = "gvm/scap-data"
DEFAULT_CERT_DATA_PATH = "gvm/cert-data"
DEFAULT_GVMD_DATA_PATH = "gvm/data-objects/gvmd/22.04/"
DEFAULT_REPORT_FORMATS_PATH = "gvm/data-objects/gvmd/22.04/report-formats"
DEFAULT_SCAN_CONFIGS_PATH = "gvm/data-objects/gvmd/22.04/scan-configs"
DEFAULT_PORT_LISTS_PATH = "gvm/data-objects/gvmd/22.04/port-lists"

DEFAULT_GVMD_LOCK_FILE_PATH = "gvm/feed-update.lock"
DEFAULT_OPENVAS_LOCK_FILE_PATH = "openvas/feed-update.lock"

DEFAULT_CONFIG_FILE = "/etc/gvm/greenbone-feed-sync.toml"
DEFAULT_USER_CONFIG_FILE = "~/.config/greenbone-feed-sync.toml"

DEFAULT_GROUP = "gvm"
DEFAULT_USER = "gvm"

DEFAULT_VERBOSITY = 2

_CONFIG = (
    (
        "destination-prefix",
        "GREENBONE_FEED_SYNC_DESTINATION_PREFIX",
        DEFAULT_DESTINATION_PREFIX,
        Path,
    ),
    ("feed-url", "GREENBONE_FEED_SYNC_URL", DEFAULT_RSYNC_URL, str),
    (
        "gvmd-data-destination",
        "GREENBONE_FEED_SYNC_GVMD_DATA_DESTINATION",
        f"{{destination-prefix}}/{DEFAULT_GVMD_DATA_PATH}",
        Path,
    ),
    (
        "gvmd-data-url",
        "GREENBONE_FEED_SYNC_GVMD_DATA_URL",
        f"{{feed-url}}{DEFAULT_GVMD_DATA_URL_PATH}",
        str,
    ),
    (
        "notus-destination",
        "GREENBONE_FEED_SYNC_NOTUS_DESTINATION",
        f"{{destination-prefix}}/{DEFAULT_NOTUS_PATH}",
        Path,
    ),
    (
        "notus-url",
        "GREENBONE_FEED_SYNC_NOTUS_URL",
        f"{{feed-url}}{DEFAULT_NOTUS_URL_PATH}",
        str,
    ),
    (
        "nasl-destination",
        "GREENBONE_FEED_SYNC_NASL_DESTINATION",
        f"{{destination-prefix}}/{DEFAULT_NASL_PATH}",
        Path,
    ),
    (
        "nasl-url",
        "GREENBONE_FEED_SYNC_NASL_URL",
        f"{{feed-url}}{DEFAULT_NASL_URL_PATH}",
        str,
    ),
    (
        "scap-data-destination",
        "GREENBONE_FEED_SYNC_SCAP_DATA_DESTINATION",
        f"{{destination-prefix}}/{DEFAULT_SCAP_DATA_PATH}",
        Path,
    ),
    (
        "scap-data-url",
        "GREENBONE_FEED_SYNC_SCAP_DATA_URL",
        f"{{feed-url}}{DEFAULT_SCAP_DATA_URL_PATH}",
        str,
    ),
    (
        "cert-data-destination",
        "GREENBONE_FEED_SYNC_CERT_DATA_DESTINATION",
        f"{{destination-prefix}}/{DEFAULT_CERT_DATA_PATH}",
        Path,
    ),
    (
        "cert-data-url",
        "GREENBONE_FEED_SYNC_CERT_DATA_URL",
        f"{{feed-url}}{DEFAULT_CERT_DATA_URL_PATH}",
        str,
    ),
    (
        "report-formats-destination",
        "GREENBONE_FEED_SYNC_REPORT_FORMATS_DESTINATION",
        f"{{destination-prefix}}/{DEFAULT_REPORT_FORMATS_PATH}",
        Path,
    ),
    (
        "report-formats-url",
        "GREENBONE_FEED_SYNC_REPORT_FORMATS_URL",
        f"{{feed-url}}{DEFAULT_REPORT_FORMATS_URL_PATH}",
        str,
    ),
    (
        "scan-configs-destination",
        "GREENBONE_FEED_SYNC_SCAN_CONFIGS_DESTINATION",
        f"{{destination-prefix}}/{DEFAULT_SCAN_CONFIGS_PATH}",
        Path,
    ),
    (
        "scan-configs-url",
        "GREENBONE_FEED_SYNC_SCAN_CONFIGS_URL",
        f"{{feed-url}}{DEFAULT_SCAN_CONFIGS_URL_PATH}",
        str,
    ),
    (
        "port-lists-destination",
        "GREENBONE_FEED_SYNC_PORT_LISTS_DESTINATION",
        f"{{destination-prefix}}/{DEFAULT_PORT_LISTS_PATH}",
        Path,
    ),
    (
        "port-lists-url",
        "GREENBONE_FEED_SYNC_PORT_LISTS_URL",
        f"{{feed-url}}{DEFAULT_PORT_LISTS_URL_PATH}",
        str,
    ),
    (
        "gvmd-lock-file",
        "GREENBONE_FEED_SYNC_GVMD_LOCK_FILE",
        f"{{destination-prefix}}/{DEFAULT_GVMD_LOCK_FILE_PATH}",
        Path,
    ),
    (
        "openvas-lock-file",
        "GREENBONE_FEED_SYNC_OPENVAS_LOCK_FILE",
        f"{{destination-prefix}}/{DEFAULT_OPENVAS_LOCK_FILE_PATH}",
        Path,
    ),
    (
        "wait-interval",
        "GREENBONE_FEED_SYNC_LOCK_WAIT_INTERVAL",
        DEFAULT_FLOCK_WAIT_INTERVAL,
        int,
    ),
    ("no-wait", "GREENBONE_FEED_SYNC_NO_WAIT", False, bool),
    (
        "compression-level",
        "GREENBONE_FEED_SYNC_COMPRESSION_LEVEL",
        DEFAULT_RSYNC_COMPRESSION_LEVEL,
        int,
    ),
    ("private-directory", "GREENBONE_FEED_SYNC_PRIVATE_DIRECTORY", None, Path),
    ("verbose", "GREENBONE_FEED_SYNC_VERBOSE", None, int),
    ("fail-fast", "GREENBONE_FEED_SYNC_FAIL_FAST", False, bool),
    ("rsync-timeout", "GREENBONE_FEED_SYNC_RSYNC_TIMEOUT", None, int),
    ("group", "GREENBONE_FEED_SYNC_GROUP", DEFAULT_GROUP, maybe_int),
    ("user", "GREENBONE_FEED_SYNC_USER", DEFAULT_USER, maybe_int),
)


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

    def _load_config(self, config_file: str) -> dict[str, Any]:
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
        config_data = self._load_config(config_file)
        self.parser.set_defaults(**_to_defaults(config_data))

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


class Config:
    """
    A class to load configuration values from the environment, config file and
    defaults.
    """

    @staticmethod
    def load(config_file: Optional[Path] = None) -> dict[str, Any]:
        """Load config values from config_file"""
        config: dict[str, Any] = {}

        if config_file:
            try:
                content = config_file.read_text(encoding="utf-8")
                config_data = tomllib.loads(content)
                config = config_data.get("greenbone-feed-sync", {})
            except IOError as e:
                raise ConfigFileError(
                    f"Can't load config file {config_file.absolute()}. "
                    f"Error was {e}."
                ) from e
            except tomllib.TOMLDecodeError as e:
                raise ConfigFileError(
                    f"Can't load config file. {config_file.absolute()} is not "
                    "a valid TOML file."
                ) from e

        values: dict[str, Any] = {}

        for config_key, env_key, default, value_type in _CONFIG:
            if env_key in os.environ:
                value = os.environ.get(env_key)
            elif config_key in config:
                value = config.get(config_key)
            elif isinstance(default, str):
                value = default.format(**values)
            else:
                value = default

            values[config_key] = None if value is None else value_type(value)

        return values
