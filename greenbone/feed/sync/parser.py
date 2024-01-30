# SPDX-FileCopyrightText: 2023-2024 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any, Optional, Sequence

from greenbone.feed.sync.__version__ import __version__
from greenbone.feed.sync.config import (
    DEFAULT_CONFIG_FILE,
    DEFAULT_USER_CONFIG_FILE,
    Config,
    ConfigDict,
    EnterpriseSettings,
    maybe_int,
)
from greenbone.feed.sync.errors import ConfigFileError


def _to_defaults(values: ConfigDict) -> dict[str, Any]:
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

        parser.add_argument(
            "--greenbone-enterprise-feed-key",
            type=Path,
            help="File to read the Greenbone Enterprise Feed key from. "
            "The key gives access to additional vulnerability tests for "
            "enterprise software among other advantages. See "
            "https://www.greenbone.net/en/feed-comparison/ for more details."
            "The default URLs are adjusted according to the data in the key."
            "If the key file does not exist it is ignored. "
            "(Default: %(default)s)",
        )

        self.parser = parser

    def _determine_enterprise_settings(
        self, enterprise_key: Path
    ) -> Optional[EnterpriseSettings]:
        if not enterprise_key or not enterprise_key.exists():
            return None

        return EnterpriseSettings.from_key(enterprise_key)

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

        config = Config()

        if config_path:
            config.load_from_config_file(config_path)

        return config

    def _set_defaults(self, config: ConfigDict) -> None:
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
        config = self._load_config(known_args.config)

        # set greenbone enterprise feed key in config if user passed one to load
        # desired key for determining the feed url
        if known_args.greenbone_enterprise_feed_key:
            config["greenbone-enterprise-feed-key"] = (
                known_args.greenbone_enterprise_feed_key
            )

        if self.parser.prog == "greenbone-nvt-sync":
            config["type"] = "nvt"
        elif self.parser.prog == "greenbone-scapdata-sync":
            config["type"] = "scap"
        elif self.parser.prog == "greenbone-certdata-sync":
            config["type"] = "cert"

        # apply defaults in config
        config.apply_settings()

        # check if a enterprise feed key is available
        enterprise_settings = self._determine_enterprise_settings(
            config["greenbone-enterprise-feed-key"]
        )

        # override feed url from key
        if enterprise_settings:
            config["feed-url"] = enterprise_settings.feed_url()

        # apply other config defaults
        config.apply_dependent_settings()

        # set config as defaults for CLI to make them visible in --help
        self._set_defaults(config)

        if known_args.help:
            self.parser.print_help()
            self.parser.exit(0)

        return self.parser.parse_args(args)
