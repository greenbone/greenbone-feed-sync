# SPDX-FileCopyrightText: 2023-2024 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import os
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    Optional,
    Protocol,
    TypeVar,
    Union,
)
from urllib.parse import urlsplit

from greenbone.feed.sync.errors import ConfigError, ConfigFileError
from greenbone.feed.sync.helper import DEFAULT_FLOCK_WAIT_INTERVAL
from greenbone.feed.sync.rsync import (
    DEFAULT_RSYNC_COMPRESSION_LEVEL,
    DEFAULT_RSYNC_URL,
)

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]


def maybe_int(value: Optional[str]) -> Union[int, str, None]:
    """
    Convert string into int if possible
    """
    try:
        value = int(value)  # type: ignore[arg-type,assignment]
    except ValueError:
        pass

    return value


DEFAULT_FEED_RELEASE = "24.10"

DEFAULT_DESTINATION_PREFIX = "/var/lib/"

DEFAULT_NASL_PATH = "openvas/plugins"
DEFAULT_NOTUS_PATH = "notus"
DEFAULT_SCAP_DATA_PATH = "gvm/scap-data"
DEFAULT_CERT_DATA_PATH = "gvm/cert-data"

DEFAULT_GVMD_LOCK_FILE_PATH = "gvm/feed-update.lock"
DEFAULT_OPENVAS_LOCK_FILE_PATH = "openvas/feed-update.lock"

DEFAULT_CONFIG_FILE = "/etc/gvm/greenbone-feed-sync.toml"
DEFAULT_USER_CONFIG_FILE = "~/.config/greenbone-feed-sync.toml"

DEFAULT_ENTERPRISE_KEY_PATH = "/etc/gvm/greenbone-enterprise-feed-key"

DEFAULT_GROUP = "gvm"
DEFAULT_USER = "gvm"

DEFAULT_VERBOSITY = 2

T = TypeVar("T")
ValuesDict = dict[str, Any]
DefaultValueCallable = Callable[[ValuesDict], Any]
ValueTypeCallable = Callable[[Any], T]


def resolve_gvmd_data_destination(values: ValuesDict) -> str:
    path = "gvm/data-objects/gvmd"
    feed_release: str = values.get("feed-release")  # type: ignore[assignment]
    try:
        str_major, str_minor = feed_release.split(".")[:2]
        major, minor = int(str_major), int(str_minor)
    except ValueError as e:
        raise ConfigError(f"Invalid feed release format: {feed_release}") from e

    return (
        f"{values['destination-prefix']}/{path}"
        if major >= 24 and minor >= 10
        else f"{values['destination-prefix']}/{path}/{feed_release}"
    )


@dataclass
class Setting(Generic[T]):
    config_key: str
    environment_key: str
    default_value: Union[str, int, bool, None]
    value_type: ValueTypeCallable[T]

    def resolve(self, values: ValuesDict) -> Optional[T]:
        value: Any
        if self.environment_key in os.environ:
            value = os.environ.get(self.environment_key)
        elif self.config_key in values:
            value = values.get(self.config_key)
        else:
            value = self.default_value

        return None if value is None else self.value_type(value)


@dataclass
class DependentSetting(Generic[T]):
    config_key: str
    environment_key: str
    default_value: DefaultValueCallable
    value_type: ValueTypeCallable[T]

    def resolve(self, values: ValuesDict) -> Optional[T]:
        if self.environment_key in os.environ:
            value = os.environ.get(self.environment_key)
        elif self.config_key in values:
            value = values.get(self.config_key)
        else:
            value = self.default_value(values)

        return None if value is None else self.value_type(value)


@dataclass
class EnterpriseSettings:
    user: Optional[str]
    host: Optional[str]
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
    Setting(
        "greenbone-enterprise-feed-key",
        "GREENBONE_FEED_SYNC_ENTERPRISE_FEED_KEY",
        DEFAULT_ENTERPRISE_KEY_PATH,
        Path,
    ),
    Setting(
        "feed-release",
        "GREENBONE_FEED_SYNC_FEED_RELEASE",
        DEFAULT_FEED_RELEASE,
        str,
    ),
)


_DEPENDENT_SETTINGS = (
    DependentSetting(
        "gvmd-data-destination",
        "GREENBONE_FEED_SYNC_GVMD_DATA_DESTINATION",
        resolve_gvmd_data_destination,
        Path,
    ),
    DependentSetting(
        "gvmd-data-url",
        "GREENBONE_FEED_SYNC_GVMD_DATA_URL",
        lambda values: f"{values['feed-url']}/data-feed/{values['feed-release']}/",
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
        lambda values: f"{values['feed-url']}/vulnerability-feed/{values['feed-release']}/vt-data/notus/",
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
        lambda values: f"{values['feed-url']}/vulnerability-feed/{values['feed-release']}/vt-data/nasl/",
        str,
    ),
    DependentSetting(
        "scap-data-destination",
        "GREENBONE_FEED_SYNC_SCAP_DATA_DESTINATION",
        lambda values: f"{values['destination-prefix']}/{DEFAULT_SCAP_DATA_PATH}",  # noqa: E501
        Path,
    ),
    DependentSetting(
        "scap-data-url",
        "GREENBONE_FEED_SYNC_SCAP_DATA_URL",
        lambda values: f"{values['feed-url']}/vulnerability-feed/{values['feed-release']}/scap-data/",
        str,
    ),
    DependentSetting(
        "cert-data-destination",
        "GREENBONE_FEED_SYNC_CERT_DATA_DESTINATION",
        lambda values: f"{values['destination-prefix']}/{DEFAULT_CERT_DATA_PATH}",  # noqa: E501
        Path,
    ),
    DependentSetting(
        "cert-data-url",
        "GREENBONE_FEED_SYNC_CERT_DATA_URL",
        lambda values: f"{values['feed-url']}/vulnerability-feed/{values['feed-release']}/cert-data/",
        str,
    ),
    DependentSetting(
        "report-formats-destination",
        "GREENBONE_FEED_SYNC_REPORT_FORMATS_DESTINATION",
        lambda values: f"{values['gvmd-data-destination']}/report-formats",
        Path,
    ),
    DependentSetting(
        "report-formats-url",
        "GREENBONE_FEED_SYNC_REPORT_FORMATS_URL",
        lambda values: f"{values['feed-url']}/data-feed/{values['feed-release']}/report-formats/",  # noqa: E501
        str,
    ),
    DependentSetting(
        "scan-configs-destination",
        "GREENBONE_FEED_SYNC_SCAN_CONFIGS_DESTINATION",
        lambda values: f"{values['gvmd-data-destination']}/scan-configs",
        Path,
    ),
    DependentSetting(
        "scan-configs-url",
        "GREENBONE_FEED_SYNC_SCAN_CONFIGS_URL",
        lambda values: f"{values['feed-url']}/data-feed/{values['feed-release']}/scan-configs/",  # noqa: E501
        str,
    ),
    DependentSetting(
        "port-lists-destination",
        "GREENBONE_FEED_SYNC_PORT_LISTS_DESTINATION",
        lambda values: f"{values['gvmd-data-destination']}/port-lists",
        Path,
    ),
    DependentSetting(
        "port-lists-url",
        "GREENBONE_FEED_SYNC_PORT_LISTS_URL",
        lambda values: f"{values['feed-url']}/data-feed/{values['feed-release']}/port-lists/",  # noqa: E501
        str,
    ),
    DependentSetting(
        "gvmd-lock-file",
        "GREENBONE_FEED_SYNC_GVMD_LOCK_FILE",
        lambda values: f"{values['destination-prefix']}/{DEFAULT_GVMD_LOCK_FILE_PATH}",  # noqa: E501
        Path,
    ),
    DependentSetting(
        "openvas-lock-file",
        "GREENBONE_FEED_SYNC_OPENVAS_LOCK_FILE",
        lambda values: f"{values['destination-prefix']}/{DEFAULT_OPENVAS_LOCK_FILE_PATH}",  # noqa: E501
        Path,
    ),
)


class ConfigDict(Protocol):
    def items(self) -> Iterable[tuple[str, Any]]: ...

    def __getitem__(self, key: str) -> Any: ...


class Config:
    """
    A class to load configuration values from the environment, config file and
    defaults.
    """

    def __init__(self) -> None:
        self._config: ValuesDict = {}

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

    def __setitem__(self, key: str, value: Any) -> None:
        self._config[key] = value

    def __len__(self) -> int:
        return len(self._config)
