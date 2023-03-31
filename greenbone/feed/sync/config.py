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

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Optional, Union
from urllib.parse import urlsplit

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


def maybe_int(value: Optional[str]) -> Union[int, str, None]:
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


@dataclass
class Setting:
    config_key: str
    environment_key: str
    default_value: Union[str, int, bool, None]
    value_type: Callable

    def resolve(self, values: dict[str, Any]) -> Any:
        if self.environment_key in os.environ:
            value = os.environ.get(self.environment_key)
        elif self.config_key in values:
            value = values.get(self.config_key)
        else:
            value = self.default_value

        return None if value is None else self.value_type(value)


@dataclass
class DependentSetting:
    config_key: str
    environment_key: str
    default_value: Callable
    value_type: Callable

    def resolve(self, values: dict[str, Any]) -> Any:
        if self.environment_key in os.environ:
            value = os.environ.get(self.environment_key)
        elif self.config_key in values:
            value = values.get(self.config_key)
        else:
            value = self.default_value(values)

        return None if value is None else self.value_type(value)


@dataclass
class EnterpriseSettings:
    user: str
    host: str
    key: Path

    @classmethod
    def from_key(cls, enterprise_key: Path) -> "EnterpriseSettings":
        with enterprise_key.open("r", encoding="utf8", errors="ignore") as f:
            line = f.readline()

        url = urlsplit(line)
        if not url.scheme:
            # ensure that url gets splitted correctly if line doesn't contain
            # an url scheme (which is the default)
            url = urlsplit(f"//{line}")

        return EnterpriseSettings(url.username, url.hostname, enterprise_key)

    def feed_url(self) -> str:
        return f"ssh://{self.user}@{self.host}/enterprise"


_SETTINGS = (
    Setting(
        "destination-prefix",
        "GREENBONE_FEED_SYNC_DESTINATION_PREFIX",
        DEFAULT_DESTINATION_PREFIX,
        Path,
    ),
    Setting("feed-url", "GREENBONE_FEED_SYNC_URL", DEFAULT_RSYNC_URL, str),
    Setting(
        "wait-interval",
        "GREENBONE_FEED_SYNC_LOCK_WAIT_INTERVAL",
        DEFAULT_FLOCK_WAIT_INTERVAL,
        int,
    ),
    Setting("no-wait", "GREENBONE_FEED_SYNC_NO_WAIT", False, bool),
    Setting(
        "compression-level",
        "GREENBONE_FEED_SYNC_COMPRESSION_LEVEL",
        DEFAULT_RSYNC_COMPRESSION_LEVEL,
        int,
    ),
    Setting(
        "private-directory", "GREENBONE_FEED_SYNC_PRIVATE_DIRECTORY", None, Path
    ),
    Setting("verbose", "GREENBONE_FEED_SYNC_VERBOSE", None, int),
    Setting("fail-fast", "GREENBONE_FEED_SYNC_FAIL_FAST", False, bool),
    Setting("rsync-timeout", "GREENBONE_FEED_SYNC_RSYNC_TIMEOUT", None, int),
    Setting("group", "GREENBONE_FEED_SYNC_GROUP", DEFAULT_GROUP, maybe_int),
    Setting("user", "GREENBONE_FEED_SYNC_USER", DEFAULT_USER, maybe_int),
)

# pylint: disable=line-too-long
_DEPENDENT_SETTINGS = (
    DependentSetting(
        "gvmd-data-destination",
        "GREENBONE_FEED_SYNC_GVMD_DATA_DESTINATION",
        lambda values: f"{values['destination-prefix']}/{DEFAULT_GVMD_DATA_PATH}",
        Path,
    ),
    DependentSetting(
        "gvmd-data-url",
        "GREENBONE_FEED_SYNC_GVMD_DATA_URL",
        lambda values: f"{values['feed-url']}{DEFAULT_GVMD_DATA_URL_PATH}",
        str,
    ),
    DependentSetting(
        "notus-destination",
        "GREENBONE_FEED_SYNC_NOTUS_DESTINATION",
        lambda values: f"{values['destination-prefix']}/{DEFAULT_NOTUS_PATH}",
        Path,
    ),
    DependentSetting(
        "notus-url",
        "GREENBONE_FEED_SYNC_NOTUS_URL",
        lambda values: f"{values['feed-url']}{DEFAULT_NOTUS_URL_PATH}",
        str,
    ),
    DependentSetting(
        "nasl-destination",
        "GREENBONE_FEED_SYNC_NASL_DESTINATION",
        lambda values: f"{values['destination-prefix']}/{DEFAULT_NASL_PATH}",
        Path,
    ),
    DependentSetting(
        "nasl-url",
        "GREENBONE_FEED_SYNC_NASL_URL",
        lambda values: f"{values['feed-url']}{DEFAULT_NASL_URL_PATH}",
        str,
    ),
    DependentSetting(
        "scap-data-destination",
        "GREENBONE_FEED_SYNC_SCAP_DATA_DESTINATION",
        lambda values: f"{values['destination-prefix']}/{DEFAULT_SCAP_DATA_PATH}",
        Path,
    ),
    DependentSetting(
        "scap-data-url",
        "GREENBONE_FEED_SYNC_SCAP_DATA_URL",
        lambda values: f"{values['feed-url']}{DEFAULT_SCAP_DATA_URL_PATH}",
        str,
    ),
    DependentSetting(
        "cert-data-destination",
        "GREENBONE_FEED_SYNC_CERT_DATA_DESTINATION",
        lambda values: f"{values['destination-prefix']}/{DEFAULT_CERT_DATA_PATH}",
        Path,
    ),
    DependentSetting(
        "cert-data-url",
        "GREENBONE_FEED_SYNC_CERT_DATA_URL",
        lambda values: f"{values['feed-url']}{DEFAULT_CERT_DATA_URL_PATH}",
        str,
    ),
    DependentSetting(
        "report-formats-destination",
        "GREENBONE_FEED_SYNC_REPORT_FORMATS_DESTINATION",
        lambda values: f"{values['destination-prefix']}/{DEFAULT_REPORT_FORMATS_PATH}",
        Path,
    ),
    DependentSetting(
        "report-formats-url",
        "GREENBONE_FEED_SYNC_REPORT_FORMATS_URL",
        lambda values: f"{values['feed-url']}{DEFAULT_REPORT_FORMATS_URL_PATH}",
        str,
    ),
    DependentSetting(
        "scan-configs-destination",
        "GREENBONE_FEED_SYNC_SCAN_CONFIGS_DESTINATION",
        lambda values: f"{values['destination-prefix']}/{DEFAULT_SCAN_CONFIGS_PATH}",
        Path,
    ),
    DependentSetting(
        "scan-configs-url",
        "GREENBONE_FEED_SYNC_SCAN_CONFIGS_URL",
        lambda values: f"{values['feed-url']}{DEFAULT_SCAN_CONFIGS_URL_PATH}",
        str,
    ),
    DependentSetting(
        "port-lists-destination",
        "GREENBONE_FEED_SYNC_PORT_LISTS_DESTINATION",
        lambda values: f"{values['destination-prefix']}/{DEFAULT_PORT_LISTS_PATH}",
        Path,
    ),
    DependentSetting(
        "port-lists-url",
        "GREENBONE_FEED_SYNC_PORT_LISTS_URL",
        lambda values: f"{values['feed-url']}{DEFAULT_PORT_LISTS_URL_PATH}",
        str,
    ),
    DependentSetting(
        "gvmd-lock-file",
        "GREENBONE_FEED_SYNC_GVMD_LOCK_FILE",
        lambda values: f"{values['destination-prefix']}/{DEFAULT_GVMD_LOCK_FILE_PATH}",
        Path,
    ),
    DependentSetting(
        "openvas-lock-file",
        "GREENBONE_FEED_SYNC_OPENVAS_LOCK_FILE",
        lambda values: f"{values['destination-prefix']}/{DEFAULT_OPENVAS_LOCK_FILE_PATH}",
        Path,
    ),
)


class Config:
    """
    A class to load configuration values from the environment, config file and
    defaults.
    """

    def __init__(self) -> None:
        self._config: dict[str, Any] = {}

    def load_from_config_file(self, config_file: Path) -> None:
        try:
            content = config_file.read_text(encoding="utf-8")
            config_data = tomllib.loads(content)
            self._config = config_data.get("greenbone-feed-sync", {})
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

    def apply_settings(self) -> None:
        for setting in _SETTINGS:
            self._config[setting.config_key] = setting.resolve(self._config)

    def apply_dependent_settings(self) -> None:
        for setting in _DEPENDENT_SETTINGS:
            self._config[setting.config_key] = setting.resolve(self._config)

    @classmethod
    def load(cls, config_file: Optional[Path] = None) -> "Config":
        """
        Load config values from config_file and apply all settings
        """
        config = cls()

        if config_file:
            config.load_from_config_file(config_file)

        config.apply_settings()
        config.apply_dependent_settings()

        return config

    def items(self) -> Iterable[tuple[str, Any]]:
        return self._config.items()

    def __getitem__(self, key: str) -> Any:
        return self._config[key]

    def __len__(self) -> int:
        return len(self._config)
