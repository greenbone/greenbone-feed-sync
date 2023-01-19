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
from typing import Any, Optional

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

DEFAULT_NOTUS_URL_PATH = "/vulnerability-feed/22.04/vt-data/notus/"
DEFAULT_NASL_URL_PATH = "/vulnerability-feed/22.04/vt-data/nasl/"
DEFAULT_SCAP_DATA_URL_PATH = "/vulnerability-feed/22.04/scap-data/"
DEFAULT_CERT_DATA_URL_PATH = "/vulnerability-feed/22.04/cert-data/"
DEFAULT_REPORT_FORMATS_URL_PATH = "/data-feed/22.04/report-formats/"
DEFAULT_SCAN_CONFIGS_URL_PATH = "/data-feed/22.04/scan-configs/"
DEFAULT_PORT_LISTS_URL_PATH = "/data-feed/22.04/port-lists/"

DEFAULT_DESTINATION_PREFIX = "/var/lib/"

DEFAULT_NASL_PATH = "{destination-prefix}openvas/plugins"
DEFAULT_NOTUS_PATH = "{destination-prefix}notus"
DEFAULT_SCAP_DATA_PATH = "{destination-prefix}gvm/scap-data"
DEFAULT_CERT_DATA_PATH = "{destination-prefix}gvm/cert-data"
DEFAULT_REPORT_FORMATS_PATH = (
    "{destination-prefix}gvm/data-objects/gvmd/22.04/report-formats"
)
DEFAULT_SCAN_CONFIGS_PATH = (
    "{destination-prefix}gvm/data-objects/gvmd/22.04/scan-configs"
)
DEFAULT_PORT_LISTS_PATH = (
    "{destination-prefix}gvm/data-objects/gvmd/22.04/port-lists"
)

DEFAULT_LOCK_FILE_PATH = "{destination-prefix}openvas/feed-update.lock"

DEFAULT_CONFIG_FILE = "/etc/gvm/greenbone-feed-sync.toml"
DEFAULT_USER_CONFIG_FILE = "~/.config/greenbone-feed-sync.toml"

_CONFIG = (
    (
        "destination-prefix",
        "GREENBONE_FEED_DESTINATION_PREFIX",
        DEFAULT_DESTINATION_PREFIX,
    ),
    ("feed-url", "GREENBONE_FEED_URL", DEFAULT_RSYNC_URL),
    (
        "notus-destination",
        "GREENBONE_FEED_NOTUS_DESTINATION",
        DEFAULT_NOTUS_PATH,
    ),
    (
        "notus-url",
        "GREENBONE_FEED_NOTUS_URL",
        f"{{feed-url}}{DEFAULT_NOTUS_URL_PATH}",
    ),
    ("nasl-destination", "GREENBONE_NASL_DESTINATION", DEFAULT_NASL_PATH),
    (
        "nasl-url",
        "GREENBONE_FEED_NASL_URL",
        f"{{feed-url}}{DEFAULT_NASL_URL_PATH}",
    ),
    (
        "scap-data-destination",
        "GREENBONE_FEED_SCAP_DATA_DESTINATION",
        DEFAULT_SCAP_DATA_PATH,
    ),
    (
        "scap-data-url",
        "GREENBONE_FEED_SCAP_DATA_URL",
        f"{{feed-url}}{DEFAULT_SCAP_DATA_URL_PATH}",
    ),
    (
        "cert-data-destination",
        "GREENBONE_FEED_CERT_DATA_DESTINATION",
        DEFAULT_CERT_DATA_PATH,
    ),
    (
        "cert-data-url",
        "GREENBONE_FEED_CERT_DATA_URL",
        f"{{feed-url}}{DEFAULT_CERT_DATA_URL_PATH}",
    ),
    (
        "report-formats-destination",
        "GREENBONE_FEED_REPORT_FORMATS_DESTINATION",
        DEFAULT_REPORT_FORMATS_PATH,
    ),
    (
        "report-formats-url",
        "GREENBONE_FEED_REPORT_FORMATS_URL",
        f"{{feed-url}}{DEFAULT_REPORT_FORMATS_URL_PATH}",
    ),
    (
        "scan-configs-destination",
        "GREENBONE_FEED_SCAN_CONFIGS_DESTINATION",
        DEFAULT_SCAN_CONFIGS_PATH,
    ),
    (
        "scan-configs-url",
        "GREENBONE_FEED_SCAN_CONFIGS_URL",
        f"{{feed-url}}{DEFAULT_SCAN_CONFIGS_URL_PATH}",
    ),
    (
        "port-lists-destination",
        "GREENBONE_FEED_PORT_LISTS_DESTINATION",
        DEFAULT_PORT_LISTS_PATH,
    ),
    (
        "port-lists-url",
        "GREENBONE_FEED_PORT_LISTS_URL",
        f"{{feed-url}}{DEFAULT_PORT_LISTS_URL_PATH}",
    ),
    ("lock_file", "GREENBONE_FEED_LOCK_FILE", DEFAULT_LOCK_FILE_PATH),
    (
        "wait-interval",
        "GREENBONE_FEED_LOCK_WAIT_INTERVAL",
        DEFAULT_FLOCK_WAIT_INTERVAL,
    ),
    ("no-wait", "GREENBONE_FEED_NO_WAIT", False),
    (
        "compression-level",
        "GREENBONE_FEED_COMPRESSION_LEVEL",
        DEFAULT_RSYNC_COMPRESSION_LEVEL,
    ),
    ("private-directory", "GREENBONE_FEED_PRIVATE_DIRECTORY", None),
    ("verbose", "GREENBONE_FEED_VERBOSE", 0),
    ("fail-fast", "GREENBONE_FEED_FAIL_FAST", False),
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

        parser.add_argument(
            "--verbose",
            "-v",
            action="count",
            default=0,
            help="Set log verbosity. `-vvv` for maximum verbosity.",
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
                "notus",
                "nasl",
                "scap",
                "cert",
                "report-format",
                "scan-config",
                "port-list",
                "nvt",
                "gvmd-data",
                "all",
            ],
            default="all",
            type=feed_type,
            help="Select which feed should be synced. (Default: %(default)s)",
        )
        parser.add_argument(
            "--feed-url",
            help="URL to download the feed data from. (Default: %(default)s)",
        )
        parser.add_argument(
            "--destination-prefix",
            help="Destination directory prefix for all downloaded data. "
            "(Default: %(default)s)",
        )
        parser.add_argument(
            "--notus-destination",
            type=Path,
            help="Destination of the downloaded notus data. Overrides "
            "`--destination-prefix`. (Default: %(default)s)",
        )
        parser.add_argument(
            "--notus-url",
            default=f"{DEFAULT_RSYNC_URL}{DEFAULT_NOTUS_URL_PATH}",
            help="URL to download the notus data from. Overrides `--feed-url`. "
            "(Default: %(default)s)",
        )
        parser.add_argument(
            "--nasl-destination",
            type=Path,
            help="Destination of the downloaded nasl data. Overrides "
            "`--destination-prefix`. (Default: %(default)s)",
        )
        parser.add_argument(
            "--nasl-url",
            default=f"{DEFAULT_RSYNC_URL}{DEFAULT_NASL_URL_PATH}",
            help="URL to download the nasl data from. Overrides `--feed-url`. "
            "(Default: %(default)s)",
        )
        parser.add_argument(
            "--scap-data-destination",
            type=Path,
            help="Destination of the downloaded SCAP data. Overrides "
            "`--destination-prefix`. (Default: %(default)s)",
        )
        parser.add_argument(
            "--scap-data-url",
            default=f"{DEFAULT_RSYNC_URL}{DEFAULT_SCAP_DATA_URL_PATH}",
            help="URL to download the SCAP data from. Overrides `--feed-url`. "
            "(Default: %(default)s)",
        )
        parser.add_argument(
            "--cert-data-destination",
            type=Path,
            help="Destination of the downloaded CERT data. Overrides "
            "`--destination-prefix`. (Default: %(default)s)",
        )
        parser.add_argument(
            "--cert-data-url",
            default=f"{DEFAULT_RSYNC_URL}{DEFAULT_CERT_DATA_URL_PATH}",
            help="URL to download the CERT data from. Overrides `--feed-url`. "
            "(Default: %(default)s)",
        )
        parser.add_argument(
            "--report-formats-destination",
            type=Path,
            help="Destination of the downloaded report format data. Overrides "
            "`--destination-prefix`. (Default: %(default)s)",
        )
        parser.add_argument(
            "--report-formats-url",
            default=f"{DEFAULT_RSYNC_URL}{DEFAULT_REPORT_FORMATS_URL_PATH}",
            help="URL to download the report format data from. Overrides "
            "`--feed-url`. (Default: %(default)s)",
        )
        parser.add_argument(
            "--scan-configs-destination",
            type=Path,
            help="Destination of the downloaded scan config data. Overrides "
            "`--destination-prefix`. (Default: %(default)s)",
        )
        parser.add_argument(
            "--scan-configs-url",
            default=f"{DEFAULT_RSYNC_URL}{DEFAULT_SCAN_CONFIGS_URL_PATH}",
            help="URL to download the scan config data from. Overrides "
            "`--feed-url`. (Default: %(default)s)",
        )
        parser.add_argument(
            "--port-lists-destination",
            type=Path,
            help="Destination of the downloaded port list data. Overrides "
            "`--destination-prefix`. (Default: %(default)s)",
        )
        parser.add_argument(
            "--port-lists-url",
            default=f"{DEFAULT_RSYNC_URL}{DEFAULT_PORT_LISTS_URL_PATH}",
            help="URL to download the port list data from. Overrides "
            "`--feed-url`. (Default: %(default)s)",
        )
        parser.add_argument(
            "--lock-file",
            "--lockfile",
            type=Path,
            help="File to use for locking the feed synchronization. "
            "Used to avoid that more then one process accesses the feed data "
            "at the same time. (Default: %(default)s)",
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

        self.parser = parser

    def _load_config(self, config_file: str) -> dict[str, Any]:
        config = Config()

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
                config_path = None

        return config.load(config_path)

    def _set_defaults(self, config_file=None) -> None:
        config_data = self._load_config(config_file)
        self.parser.set_defaults(**_to_defaults(config_data))

    def parse_arguments(self, args=None) -> Namespace:
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

    def __init__(self) -> None:
        self._config = {}

    def load(self, config_file: Optional[Path] = None) -> dict[str, Any]:
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

        for config_key, env_key, default in _CONFIG:
            if env_key in os.environ:
                values[config_key] = os.environ.get(env_key)
            elif config_key in config:
                values[config_key] = config.get(config_key)
            elif isinstance(default, str):
                values[config_key] = default.format(**values)
            else:
                values[config_key] = default

        return values
