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

# pylint: disable=line-too-long, too-many-lines

import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import MagicMock, patch

from greenbone.feed.sync.errors import ConfigFileError
from greenbone.feed.sync.helper import DEFAULT_FLOCK_WAIT_INTERVAL
from greenbone.feed.sync.parser import (
    DEFAULT_CERT_DATA_PATH,
    DEFAULT_CERT_DATA_URL_PATH,
    DEFAULT_CONFIG_FILE,
    DEFAULT_DESTINATION_PREFIX,
    DEFAULT_GROUP,
    DEFAULT_GVMD_DATA_PATH,
    DEFAULT_GVMD_DATA_URL_PATH,
    DEFAULT_GVMD_LOCK_FILE_PATH,
    DEFAULT_NASL_PATH,
    DEFAULT_NASL_URL_PATH,
    DEFAULT_NOTUS_PATH,
    DEFAULT_NOTUS_URL_PATH,
    DEFAULT_OPENVAS_LOCK_FILE_PATH,
    DEFAULT_PORT_LISTS_PATH,
    DEFAULT_PORT_LISTS_URL_PATH,
    DEFAULT_REPORT_FORMATS_PATH,
    DEFAULT_REPORT_FORMATS_URL_PATH,
    DEFAULT_SCAN_CONFIGS_PATH,
    DEFAULT_SCAN_CONFIGS_URL_PATH,
    DEFAULT_SCAP_DATA_PATH,
    DEFAULT_SCAP_DATA_URL_PATH,
    DEFAULT_USER,
    DEFAULT_USER_CONFIG_FILE,
    CliParser,
    Config,
    feed_type,
)
from greenbone.feed.sync.rsync import (
    DEFAULT_RSYNC_COMPRESSION_LEVEL,
    DEFAULT_RSYNC_URL,
)


class FeedTypeTestCase(unittest.TestCase):
    def test_nvt(self):
        self.assertEqual("nvt", feed_type("nvt"))
        self.assertEqual("nvt", feed_type("nvts"))
        self.assertEqual("nvt", feed_type("NVT"))
        self.assertEqual("nvt", feed_type("NVTS"))

    def test_report_format(self):
        self.assertEqual("report-format", feed_type("report-format"))
        self.assertEqual("report-format", feed_type("report-formats"))
        self.assertEqual("report-format", feed_type("report_format"))
        self.assertEqual("report-format", feed_type("report_formats"))
        self.assertEqual("report-format", feed_type("REPORT_FORMAT"))
        self.assertEqual("report-format", feed_type("REPORT_FORMATS"))
        self.assertEqual("report-format", feed_type("REPORT-FORMAT"))
        self.assertEqual("report-format", feed_type("REPORT-FORMATS"))

    def test_port_list(self):
        self.assertEqual("port-list", feed_type("port-list"))
        self.assertEqual("port-list", feed_type("port-lists"))
        self.assertEqual("port-list", feed_type("port_list"))
        self.assertEqual("port-list", feed_type("port_lists"))
        self.assertEqual("port-list", feed_type("PORT_LIST"))
        self.assertEqual("port-list", feed_type("PORT_LISTS"))
        self.assertEqual("port-list", feed_type("PORT-LIST"))
        self.assertEqual("port-list", feed_type("PORT-LISTS"))

    def test_scan_config(self):
        self.assertEqual("scan-config", feed_type("scan-config"))
        self.assertEqual("scan-config", feed_type("scan-configs"))
        self.assertEqual("scan-config", feed_type("scan_config"))
        self.assertEqual("scan-config", feed_type("scan_configs"))
        self.assertEqual("scan-config", feed_type("SCAN_CONFIG"))
        self.assertEqual("scan-config", feed_type("SCAN_CONFIGS"))
        self.assertEqual("scan-config", feed_type("SCAN-CONFIG"))
        self.assertEqual("scan-config", feed_type("SCAN-CONFIGS"))

    def test_gvmd_data(self):
        self.assertEqual("gvmd-data", feed_type("gvmd-data"))
        self.assertEqual("gvmd-data", feed_type("gvmd_data"))
        self.assertEqual("gvmd-data", feed_type("GVMD-DATA"))
        self.assertEqual("gvmd-data", feed_type("GVMD_DATA"))


class ConfigTestCase(unittest.TestCase):
    def test_defaults(self):
        values = Config.load()

        self.assertEqual(len(values), 29)
        self.assertEqual(
            values["destination-prefix"], Path(DEFAULT_DESTINATION_PREFIX)
        )
        self.assertEqual(
            values["gvmd-data-destination"],
            Path(DEFAULT_DESTINATION_PREFIX) / DEFAULT_GVMD_DATA_PATH,
        )
        self.assertEqual(
            values["gvmd-data-url"],
            f"{DEFAULT_RSYNC_URL}{DEFAULT_GVMD_DATA_URL_PATH}",
        )
        self.assertEqual(values["feed-url"], DEFAULT_RSYNC_URL)
        self.assertEqual(
            values["notus-destination"],
            Path(DEFAULT_DESTINATION_PREFIX) / DEFAULT_NOTUS_PATH,
        )
        self.assertEqual(
            values["notus-url"], f"{DEFAULT_RSYNC_URL}{DEFAULT_NOTUS_URL_PATH}"
        )
        self.assertEqual(
            values["nasl-destination"],
            Path(DEFAULT_DESTINATION_PREFIX) / DEFAULT_NASL_PATH,
        )
        self.assertEqual(
            values["nasl-url"], f"{DEFAULT_RSYNC_URL}{DEFAULT_NASL_URL_PATH}"
        )
        self.assertEqual(
            values["scap-data-destination"],
            Path(DEFAULT_DESTINATION_PREFIX) / DEFAULT_SCAP_DATA_PATH,
        )
        self.assertEqual(
            values["scap-data-url"],
            f"{DEFAULT_RSYNC_URL}{DEFAULT_SCAP_DATA_URL_PATH}",
        )
        self.assertEqual(
            values["cert-data-destination"],
            Path(DEFAULT_DESTINATION_PREFIX) / DEFAULT_CERT_DATA_PATH,
        )
        self.assertEqual(
            values["cert-data-url"],
            f"{DEFAULT_RSYNC_URL}{DEFAULT_CERT_DATA_URL_PATH}",
        )
        self.assertEqual(
            values["report-formats-destination"],
            Path(DEFAULT_DESTINATION_PREFIX) / DEFAULT_REPORT_FORMATS_PATH,
        )
        self.assertEqual(
            values["report-formats-url"],
            f"{DEFAULT_RSYNC_URL}{DEFAULT_REPORT_FORMATS_URL_PATH}",
        )
        self.assertEqual(
            values["scan-configs-destination"],
            Path(DEFAULT_DESTINATION_PREFIX) / DEFAULT_SCAN_CONFIGS_PATH,
        )
        self.assertEqual(
            values["scan-configs-url"],
            f"{DEFAULT_RSYNC_URL}{DEFAULT_SCAN_CONFIGS_URL_PATH}",
        )
        self.assertEqual(
            values["port-lists-destination"],
            Path(DEFAULT_DESTINATION_PREFIX) / DEFAULT_PORT_LISTS_PATH,
        )
        self.assertEqual(
            values["port-lists-url"],
            f"{DEFAULT_RSYNC_URL}{DEFAULT_PORT_LISTS_URL_PATH}",
        )
        self.assertEqual(
            values["gvmd-lock-file"],
            Path(DEFAULT_DESTINATION_PREFIX) / DEFAULT_GVMD_LOCK_FILE_PATH,
        )
        self.assertEqual(
            values["openvas-lock-file"],
            Path(DEFAULT_DESTINATION_PREFIX) / DEFAULT_OPENVAS_LOCK_FILE_PATH,
        )
        self.assertEqual(values["wait-interval"], DEFAULT_FLOCK_WAIT_INTERVAL)
        self.assertFalse(values["no-wait"])
        self.assertEqual(
            values["compression-level"], DEFAULT_RSYNC_COMPRESSION_LEVEL
        )
        self.assertIsNone(values["private-directory"])
        self.assertIsNone(values["verbose"])
        self.assertFalse(values["fail-fast"])
        self.assertIsNone(values["rsync-timeout"])
        self.assertEqual(values["group"], DEFAULT_GROUP)
        self.assertEqual(values["user"], DEFAULT_USER)

    def test_config_file(self):
        content = """[greenbone-feed-sync]
destination-prefix = "/opt/lib"
feed-url = "rsync://lorem.ipsum"
gvmd-data-destination = "/usr/lib/gvmd-data"
gvmd-data-url = "rsync://foo.bar/gvmd-data"
notus-destination = "/usr/lib/notus"
notus-url = "rsync://foo.bar/notus"
nasl-destination = "/usr/lib/openvas/plugins/"
nasl-url = "rsync://foo.bar/nasl"
scap-data-destination = "/usr/lib/scap-data"
scap-data-url = "rsync://foo.bar/scap-data"
cert-data-destination = "/usr/lib/cert-data"
cert-data-url = "rsync://foo.bar/cert-data"
report-formats-destination = "/usr/lib/report-formats"
report-formats-url = "rsync://foo.bar/report-formats"
scan-configs-destination = "/usr/lib/scan-configs"
scan-configs-url = "rsync://foo.bar/scan-configs"
port-lists-destination = "/usr/lib/port-lists"
port-lists-url = "rsync://foo.bar/port-lists"
openvas-lock-file = "/usr/lib/openvas.lock"
gvmd-lock-file = "/usr/lib/gvmd.lock"
wait-interval = 100
no-wait = true
compression-level = 1
private-directory = "keep-this"
verbose = 5
fail-fast = true
rsync-timeout = 120
group = "foo"
user = "bar"
"""
        path_mock = MagicMock(spec=Path)
        path_mock.read_text.return_value = content

        values = Config.load(path_mock)

        self.assertEqual(values["destination-prefix"], Path("/opt/lib"))
        self.assertEqual(values["feed-url"], "rsync://lorem.ipsum")
        self.assertEqual(
            values["gvmd-data-destination"], Path("/usr/lib/gvmd-data")
        )
        self.assertEqual(values["gvmd-data-url"], "rsync://foo.bar/gvmd-data")
        self.assertEqual(
            values["nasl-destination"], Path("/usr/lib/openvas/plugins")
        )
        self.assertEqual(values["notus-destination"], Path("/usr/lib/notus"))
        self.assertEqual(values["notus-url"], "rsync://foo.bar/notus")
        self.assertEqual(
            values["nasl-destination"], Path("/usr/lib/openvas/plugins")
        )
        self.assertEqual(values["nasl-url"], "rsync://foo.bar/nasl")
        self.assertEqual(
            values["scap-data-destination"], Path("/usr/lib/scap-data")
        )
        self.assertEqual(values["scap-data-url"], "rsync://foo.bar/scap-data")
        self.assertEqual(
            values["cert-data-destination"], Path("/usr/lib/cert-data")
        )
        self.assertEqual(values["cert-data-url"], "rsync://foo.bar/cert-data")
        self.assertEqual(
            values["report-formats-destination"],
            Path("/usr/lib/report-formats"),
        )
        self.assertEqual(
            values["report-formats-url"], "rsync://foo.bar/report-formats"
        )
        self.assertEqual(
            values["scan-configs-destination"],
            Path("/usr/lib/scan-configs"),
        )
        self.assertEqual(
            values["scan-configs-url"], "rsync://foo.bar/scan-configs"
        )
        self.assertEqual(
            values["port-lists-destination"],
            Path("/usr/lib/port-lists"),
        )
        self.assertEqual(values["port-lists-url"], "rsync://foo.bar/port-lists")
        self.assertEqual(
            values["openvas-lock-file"],
            Path("/usr/lib/openvas.lock"),
        )
        self.assertEqual(values["gvmd-lock-file"], Path("/usr/lib/gvmd.lock"))
        self.assertEqual(values["wait-interval"], 100)
        self.assertTrue(values["no-wait"])
        self.assertEqual(values["compression-level"], 1)
        self.assertEqual(values["private-directory"], Path("keep-this"))
        self.assertEqual(values["verbose"], 5)
        self.assertTrue(values["fail-fast"])
        self.assertEqual(values["rsync-timeout"], 120)
        self.assertEqual(values["group"], "foo")
        self.assertEqual(values["user"], "bar")

    def test_destination_prefix(self):
        content = """[greenbone-feed-sync]
destination-prefix = "/opt/lib/"
"""

        path_mock = MagicMock(spec=Path)
        path_mock.read_text.return_value = content

        values = Config.load(path_mock)

        self.assertEqual(values["destination-prefix"], Path("/opt/lib"))
        self.assertEqual(
            values["gvmd-data-destination"],
            Path("/opt/lib/gvm/data-objects/gvmd/22.04"),
        )
        self.assertEqual(values["notus-destination"], Path("/opt/lib/notus"))
        self.assertEqual(
            values["nasl-destination"], Path("/opt/lib/openvas/plugins")
        )
        self.assertEqual(
            values["scap-data-destination"], Path("/opt/lib/gvm/scap-data")
        )
        self.assertEqual(
            values["cert-data-destination"], Path("/opt/lib/gvm/cert-data")
        )
        self.assertEqual(
            values["report-formats-destination"],
            Path("/opt/lib/gvm/data-objects/gvmd/22.04/report-formats"),
        )
        self.assertEqual(
            values["scan-configs-destination"],
            Path("/opt/lib/gvm/data-objects/gvmd/22.04/scan-configs"),
        )
        self.assertEqual(
            values["port-lists-destination"],
            Path("/opt/lib/gvm/data-objects/gvmd/22.04/port-lists"),
        )
        self.assertEqual(
            values["openvas-lock-file"],
            Path("/opt/lib/openvas/feed-update.lock"),
        )
        self.assertEqual(
            values["gvmd-lock-file"], Path("/opt/lib/gvm/feed-update.lock")
        )

    def test_feed_url(self):
        content = """[greenbone-feed-sync]
feed-url = "rsync://foo.bar"
"""
        path_mock = MagicMock(spec=Path)
        path_mock.read_text.return_value = content

        values = Config.load(path_mock)

        self.assertEqual(values["feed-url"], "rsync://foo.bar")
        self.assertEqual(
            values["gvmd-data-url"],
            "rsync://foo.bar/data-feed/22.04/",
        )
        self.assertEqual(
            values["notus-url"],
            "rsync://foo.bar/vulnerability-feed/22.04/vt-data/notus/",
        )
        self.assertEqual(
            values["nasl-url"],
            "rsync://foo.bar/vulnerability-feed/22.04/vt-data/nasl/",
        )
        self.assertEqual(
            values["scap-data-url"],
            "rsync://foo.bar/vulnerability-feed/22.04/scap-data/",
        )
        self.assertEqual(
            values["cert-data-url"],
            "rsync://foo.bar/vulnerability-feed/22.04/cert-data/",
        )
        self.assertEqual(
            values["report-formats-url"],
            "rsync://foo.bar/data-feed/22.04/report-formats/",
        )
        self.assertEqual(
            values["scan-configs-url"],
            "rsync://foo.bar/data-feed/22.04/scan-configs/",
        )
        self.assertEqual(
            values["port-lists-url"],
            "rsync://foo.bar/data-feed/22.04/port-lists/",
        )

    @patch.dict(
        "os.environ",
        {
            "GREENBONE_FEED_SYNC_DESTINATION_PREFIX": "/opt/lib",
            "GREENBONE_FEED_SYNC_URL": "rsync://lorem.ipsum",
            "GREENBONE_FEED_SYNC_GVMD_DATA_DESTINATION": "/usr/lib/gvmd-data",
            "GREENBONE_FEED_SYNC_GVMD_DATA_URL": "rsync://foo.bar/gvmd-data",
            "GREENBONE_FEED_SYNC_NOTUS_DESTINATION": "/usr/lib/notus",
            "GREENBONE_FEED_SYNC_NOTUS_URL": "rsync://foo.bar/notus",
            "GREENBONE_FEED_SYNC_NASL_DESTINATION": "/usr/lib/openvas/plugins/",
            "GREENBONE_FEED_SYNC_NASL_URL": "rsync://foo.bar/nasl",
            "GREENBONE_FEED_SYNC_SCAP_DATA_DESTINATION": "/usr/lib/scap-data",
            "GREENBONE_FEED_SYNC_SCAP_DATA_URL": "rsync://foo.bar/scap-data",
            "GREENBONE_FEED_SYNC_CERT_DATA_DESTINATION": "/usr/lib/cert-data",
            "GREENBONE_FEED_SYNC_CERT_DATA_URL": "rsync://foo.bar/cert-data",
            "GREENBONE_FEED_SYNC_REPORT_FORMATS_DESTINATION": "/usr/lib/report-formats",
            "GREENBONE_FEED_SYNC_REPORT_FORMATS_URL": "rsync://foo.bar/report-formats",
            "GREENBONE_FEED_SYNC_SCAN_CONFIGS_DESTINATION": "/usr/lib/scan-configs",
            "GREENBONE_FEED_SYNC_SCAN_CONFIGS_URL": "rsync://foo.bar/scan-configs",
            "GREENBONE_FEED_SYNC_PORT_LISTS_DESTINATION": "/usr/lib/port-lists",
            "GREENBONE_FEED_SYNC_PORT_LISTS_URL": "rsync://foo.bar/port-lists",
            "GREENBONE_FEED_SYNC_OPENVAS_LOCK_FILE": "/usr/lib/openvas.lock",
            "GREENBONE_FEED_SYNC_GVMD_LOCK_FILE": "/usr/lib/gvmd.lock",
            "GREENBONE_FEED_SYNC_LOCK_WAIT_INTERVAL": "100",
            "GREENBONE_FEED_SYNC_NO_WAIT": "1",
            "GREENBONE_FEED_SYNC_COMPRESSION_LEVEL": "1",
            "GREENBONE_FEED_SYNC_PRIVATE_DIRECTORY": "keep-this",
            "GREENBONE_FEED_SYNC_VERBOSE": "5",
            "GREENBONE_FEED_SYNC_FAIL_FAST": "1",
            "GREENBONE_FEED_SYNC_RSYNC_TIMEOUT": "120",
            "GREENBONE_FEED_SYNC_GROUP": "123",
            "GREENBONE_FEED_SYNC_USER": "321",
        },
    )
    def test_environment(self):
        values = Config.load()

        self.assertEqual(values["destination-prefix"], Path("/opt/lib"))
        self.assertEqual(values["feed-url"], "rsync://lorem.ipsum")
        self.assertEqual(
            values["gvmd-data-destination"], Path("/usr/lib/gvmd-data")
        )
        self.assertEqual(values["gvmd-data-url"], "rsync://foo.bar/gvmd-data")
        self.assertEqual(values["notus-destination"], Path("/usr/lib/notus"))
        self.assertEqual(values["notus-url"], "rsync://foo.bar/notus")
        self.assertEqual(
            values["nasl-destination"], Path("/usr/lib/openvas/plugins")
        )
        self.assertEqual(values["nasl-url"], "rsync://foo.bar/nasl")
        self.assertEqual(
            values["scap-data-destination"], Path("/usr/lib/scap-data")
        )
        self.assertEqual(values["scap-data-url"], "rsync://foo.bar/scap-data")
        self.assertEqual(
            values["cert-data-destination"], Path("/usr/lib/cert-data")
        )
        self.assertEqual(values["cert-data-url"], "rsync://foo.bar/cert-data")
        self.assertEqual(
            values["report-formats-destination"],
            Path("/usr/lib/report-formats"),
        )
        self.assertEqual(
            values["report-formats-url"], "rsync://foo.bar/report-formats"
        )
        self.assertEqual(
            values["scan-configs-destination"],
            Path("/usr/lib/scan-configs"),
        )
        self.assertEqual(
            values["scan-configs-url"], "rsync://foo.bar/scan-configs"
        )
        self.assertEqual(
            values["port-lists-destination"],
            Path("/usr/lib/port-lists"),
        )
        self.assertEqual(values["port-lists-url"], "rsync://foo.bar/port-lists")
        self.assertEqual(
            values["openvas-lock-file"],
            Path("/usr/lib/openvas.lock"),
        )
        self.assertEqual(values["gvmd-lock-file"], Path("/usr/lib/gvmd.lock"))
        self.assertEqual(values["wait-interval"], 100)
        self.assertTrue(values["no-wait"])
        self.assertEqual(values["compression-level"], 1)
        self.assertEqual(values["private-directory"], Path("keep-this"))
        self.assertEqual(values["verbose"], 5)
        self.assertTrue(values["fail-fast"])
        self.assertEqual(values["rsync-timeout"], 120)
        self.assertEqual(values["group"], 123)
        self.assertEqual(values["user"], 321)

    @patch.dict(
        "os.environ",
        {
            "GREENBONE_FEED_SYNC_DESTINATION_PREFIX": "/opt/lib",
            "GREENBONE_FEED_SYNC_URL": "rsync://lorem.ipsum",
            "GREENBONE_FEED_SYNC_GVMD_DATA_DESTINATION": "/usr/lib/gvmd-data",
            "GREENBONE_FEED_SYNC_GVMD_DATA_URL": "rsync://foo.bar/gvmd-data",
            "GREENBONE_FEED_SYNC_NOTUS_DESTINATION": "/usr/lib/notus",
            "GREENBONE_FEED_SYNC_NOTUS_URL": "rsync://foo.bar/notus",
            "GREENBONE_FEED_SYNC_NASL_DESTINATION": "/usr/lib/openvas/plugins/",
            "GREENBONE_FEED_SYNC_NASL_URL": "rsync://foo.bar/nasl",
            "GREENBONE_FEED_SYNC_SCAP_DATA_DESTINATION": "/usr/lib/scap-data",
            "GREENBONE_FEED_SYNC_SCAP_DATA_URL": "rsync://foo.bar/scap-data",
            "GREENBONE_FEED_SYNC_CERT_DATA_DESTINATION": "/usr/lib/cert-data",
            "GREENBONE_FEED_SYNC_CERT_DATA_URL": "rsync://foo.bar/cert-data",
            "GREENBONE_FEED_SYNC_REPORT_FORMATS_DESTINATION": "/usr/lib/report-formats",
            "GREENBONE_FEED_SYNC_REPORT_FORMATS_URL": "rsync://foo.bar/report-formats",
            "GREENBONE_FEED_SYNC_SCAN_CONFIGS_DESTINATION": "/usr/lib/scan-configs",
            "GREENBONE_FEED_SYNC_SCAN_CONFIGS_URL": "rsync://foo.bar/scan-configs",
            "GREENBONE_FEED_SYNC_PORT_LISTS_DESTINATION": "/usr/lib/port-lists",
            "GREENBONE_FEED_SYNC_PORT_LISTS_URL": "rsync://foo.bar/port-lists",
            "GREENBONE_FEED_SYNC_OPENVAS_LOCK_FILE": "/usr/lib/openvas.lock",
            "GREENBONE_FEED_SYNC_GVMD_LOCK_FILE": "/usr/lib/gvmd.lock",
            "GREENBONE_FEED_SYNC_LOCK_WAIT_INTERVAL": "100",
            "GREENBONE_FEED_SYNC_NO_WAIT": "1",
            "GREENBONE_FEED_SYNC_COMPRESSION_LEVEL": "1",
            "GREENBONE_FEED_SYNC_PRIVATE_DIRECTORY": "keep-this",
            "GREENBONE_FEED_SYNC_VERBOSE": "5",
            "GREENBONE_FEED_SYNC_FAIL_FAST": "1",
            "GREENBONE_FEED_SYNC_RSYNC_TIMEOUT": "120",
        },
    )
    def test_environment_overrides_config_file(self):
        content = """[greenbone-feed-sync]
destination-prefix = "/svr/lib"
feed-url = "rsync://ipsum.lorem"
gvmd-data-destination = "/root/notus"
gvmd-data-url = "rsync://bar.foo/notus"
notus-destination = "/root/notus"
notus-url = "rsync://bar.foo/notus"
nasl-destination = "/root/openvas/plugins/"
nasl-url = "rsync://bar.foo/nasl"
scap-data-destination = "/root/scap-data"
scap-data-url = "rsync://bar.foo/scap-data"
cert-data-destination = "/root/cert-data"
cert-data-url = "rsync://bar.foo/cert-data"
report-formats-destination = "/root/report-formats"
report-formats-url = "rsync://bar.foo/report-formats"
scan-configs-destination = "/root/scan-configs"
scan-configs-url = "rsync://bar.foo/scan-configs"
port-lists-destination = "/root/port-lists"
port-lists-url = "rsync://bar.foo/port-lists"
openvas-lock-file = "/root/openvas.lock"
gvmd-lock-file = "/root/gvmd.lock"
wait-interval = 99
no-wait = false
compression-level = 7
private-directory = "private"
verbose = 99
fail-fast = false
rsync-timeout = 360
"""
        path_mock = MagicMock(spec=Path)
        path_mock.read_text.return_value = content

        values = Config.load(path_mock)

        self.assertEqual(values["destination-prefix"], Path("/opt/lib"))
        self.assertEqual(values["feed-url"], "rsync://lorem.ipsum")
        self.assertEqual(
            values["gvmd-data-destination"], Path("/usr/lib/gvmd-data")
        )
        self.assertEqual(values["gvmd-data-url"], "rsync://foo.bar/gvmd-data")
        self.assertEqual(values["notus-destination"], Path("/usr/lib/notus"))
        self.assertEqual(values["notus-url"], "rsync://foo.bar/notus")
        self.assertEqual(
            values["nasl-destination"], Path("/usr/lib/openvas/plugins")
        )
        self.assertEqual(values["nasl-url"], "rsync://foo.bar/nasl")
        self.assertEqual(
            values["scap-data-destination"], Path("/usr/lib/scap-data")
        )
        self.assertEqual(values["scap-data-url"], "rsync://foo.bar/scap-data")
        self.assertEqual(
            values["cert-data-destination"], Path("/usr/lib/cert-data")
        )
        self.assertEqual(values["cert-data-url"], "rsync://foo.bar/cert-data")
        self.assertEqual(
            values["report-formats-destination"],
            Path("/usr/lib/report-formats"),
        )
        self.assertEqual(
            values["report-formats-url"], "rsync://foo.bar/report-formats"
        )
        self.assertEqual(
            values["scan-configs-destination"],
            Path("/usr/lib/scan-configs"),
        )
        self.assertEqual(
            values["scan-configs-url"], "rsync://foo.bar/scan-configs"
        )
        self.assertEqual(
            values["port-lists-destination"],
            Path("/usr/lib/port-lists"),
        )
        self.assertEqual(values["port-lists-url"], "rsync://foo.bar/port-lists")
        self.assertEqual(
            values["openvas-lock-file"],
            Path("/usr/lib/openvas.lock"),
        )
        self.assertEqual(values["gvmd-lock-file"], Path("/usr/lib/gvmd.lock"))
        self.assertEqual(values["wait-interval"], 100)
        self.assertTrue(values["no-wait"])
        self.assertEqual(values["compression-level"], 1)
        self.assertEqual(values["private-directory"], Path("keep-this"))
        self.assertEqual(values["verbose"], 5)
        self.assertTrue(values["fail-fast"])
        self.assertEqual(values["rsync-timeout"], 120)

    def test_invalid_toml(self):
        content = "This is not TOML"
        path_mock = MagicMock(spec=Path)
        path_mock.read_text.return_value = content
        path_mock.absolute.return_value = "/foo/bar.toml"

        with self.assertRaisesRegex(
            ConfigFileError,
            "Can't load config file. /foo/bar.toml is not a valid TOML file.",
        ):
            Config.load(path_mock)

    def test_load_ioerror(self):
        with self.assertRaisesRegex(
            ConfigFileError,
            r"Can't load config file .*foo\.toml\. Error was .*",
        ):
            Config.load(Path("foo.toml"))


class CliParserTestCase(unittest.TestCase):
    def test_output_group(self):
        parser = CliParser()

        with redirect_stderr(io.StringIO()) as f, self.assertRaises(SystemExit):
            parser.parse_arguments(["-vvv", "--quiet"])

        self.assertIn(
            "argument --quiet: not allowed with argument --verbose/-v",
            f.getvalue(),
        )

    def test_wait_group(self):
        parser = CliParser()

        with redirect_stderr(io.StringIO()) as f, self.assertRaises(SystemExit):
            parser.parse_arguments(["--no-wait", "--wait-interval", "20"])

        self.assertIn(
            "argument --wait-interval: not allowed with argument --no-wait",
            f.getvalue(),
        )

    def test_defaults(self):
        parser = CliParser()
        args = parser.parse_arguments([])
        self.assertEqual(
            args.destination_prefix, Path(DEFAULT_DESTINATION_PREFIX)
        )
        self.assertEqual(args.feed_url, DEFAULT_RSYNC_URL)
        self.assertEqual(
            args.gvmd_data_destination,
            Path(DEFAULT_DESTINATION_PREFIX) / DEFAULT_GVMD_DATA_PATH,
        )
        self.assertEqual(
            args.gvmd_data_url,
            f"{DEFAULT_RSYNC_URL}{DEFAULT_GVMD_DATA_URL_PATH}",
        )
        self.assertEqual(
            args.notus_destination,
            Path(DEFAULT_DESTINATION_PREFIX) / DEFAULT_NOTUS_PATH,
        )
        self.assertEqual(
            args.notus_url, f"{DEFAULT_RSYNC_URL}{DEFAULT_NOTUS_URL_PATH}"
        )
        self.assertEqual(
            args.nasl_destination,
            Path(DEFAULT_DESTINATION_PREFIX) / DEFAULT_NASL_PATH,
        )
        self.assertEqual(
            args.nasl_url, f"{DEFAULT_RSYNC_URL}{DEFAULT_NASL_URL_PATH}"
        )
        self.assertEqual(
            args.scap_data_destination,
            Path(DEFAULT_DESTINATION_PREFIX) / DEFAULT_SCAP_DATA_PATH,
        )
        self.assertEqual(
            args.scap_data_url,
            f"{DEFAULT_RSYNC_URL}{DEFAULT_SCAP_DATA_URL_PATH}",
        )
        self.assertEqual(
            args.cert_data_destination,
            Path(DEFAULT_DESTINATION_PREFIX) / DEFAULT_CERT_DATA_PATH,
        )
        self.assertEqual(
            args.cert_data_url,
            f"{DEFAULT_RSYNC_URL}{DEFAULT_CERT_DATA_URL_PATH}",
        )
        self.assertEqual(
            args.report_formats_destination,
            Path(DEFAULT_DESTINATION_PREFIX) / DEFAULT_REPORT_FORMATS_PATH,
        )
        self.assertEqual(
            args.report_formats_url,
            f"{DEFAULT_RSYNC_URL}{DEFAULT_REPORT_FORMATS_URL_PATH}",
        )
        self.assertEqual(
            args.scan_configs_destination,
            Path(DEFAULT_DESTINATION_PREFIX) / DEFAULT_SCAN_CONFIGS_PATH,
        )
        self.assertEqual(
            args.scan_configs_url,
            f"{DEFAULT_RSYNC_URL}{DEFAULT_SCAN_CONFIGS_URL_PATH}",
        )
        self.assertEqual(
            args.port_lists_destination,
            Path(DEFAULT_DESTINATION_PREFIX) / DEFAULT_PORT_LISTS_PATH,
        )
        self.assertEqual(
            args.port_lists_url,
            f"{DEFAULT_RSYNC_URL}{DEFAULT_PORT_LISTS_URL_PATH}",
        )
        self.assertEqual(
            args.gvmd_lock_file,
            Path(DEFAULT_DESTINATION_PREFIX) / DEFAULT_GVMD_LOCK_FILE_PATH,
        )
        self.assertEqual(
            args.openvas_lock_file,
            Path(DEFAULT_DESTINATION_PREFIX) / DEFAULT_OPENVAS_LOCK_FILE_PATH,
        )
        self.assertEqual(args.wait_interval, DEFAULT_FLOCK_WAIT_INTERVAL)
        self.assertFalse(args.no_wait)
        self.assertEqual(
            args.compression_level, DEFAULT_RSYNC_COMPRESSION_LEVEL
        )
        self.assertIsNone(args.private_directory)
        self.assertIsNone(args.verbose)
        self.assertFalse(args.fail_fast)
        self.assertIsNone(args.rsync_timeout)

    def test_help(self):
        parser = CliParser()

        with redirect_stdout(io.StringIO()) as f, self.assertRaises(
            SystemExit
        ) as cm:
            parser.parse_arguments(["--help"])

        self.assertEqual(cm.exception.code, 0)
        self.assertTrue(f.getvalue().startswith("usage: "))

    def test_verbose(self):
        parser = CliParser()

        args = parser.parse_arguments(["-v"])
        self.assertEqual(args.verbose, 1)

        args = parser.parse_arguments(["--verbose"])
        self.assertEqual(args.verbose, 1)

        args = parser.parse_arguments(["-vv"])
        self.assertEqual(args.verbose, 2)

        args = parser.parse_arguments(["-vvv"])
        self.assertEqual(args.verbose, 3)

        args = parser.parse_arguments(["-vvvv"])
        self.assertEqual(args.verbose, 4)

    def test_quiet(self):
        parser = CliParser()
        args = parser.parse_arguments(["--quiet"])
        self.assertTrue(args.quiet)

    @patch("greenbone.feed.sync.parser.Path")
    def test_use_default_config_files(self, path_mock: Path):
        path_mock_instance = path_mock.return_value
        path_mock_instance.expanduser.return_value = path_mock_instance
        path_mock_instance.resolve.return_value = path_mock_instance
        path_mock_instance.exists.return_value = False

        parser = CliParser()
        parser.parse_arguments([])

        path_mock.assert_any_call(DEFAULT_USER_CONFIG_FILE)
        path_mock.assert_any_call(DEFAULT_CONFIG_FILE)

    def test_private_directory(self):
        parser = CliParser()
        args = parser.parse_arguments(["--private-directory", "foobar"])
        self.assertEqual(args.private_directory, Path("foobar"))

    def test_compression_level(self):
        parser = CliParser()
        args = parser.parse_arguments(["--compression-level", "0"])
        self.assertEqual(args.compression_level, 0)

        args = parser.parse_arguments(["--compression-level", "1"])
        self.assertEqual(args.compression_level, 1)

        args = parser.parse_arguments(["--compression-level", "2"])
        self.assertEqual(args.compression_level, 2)

        args = parser.parse_arguments(["--compression-level", "3"])
        self.assertEqual(args.compression_level, 3)

        args = parser.parse_arguments(["--compression-level", "4"])
        self.assertEqual(args.compression_level, 4)

        args = parser.parse_arguments(["--compression-level", "5"])
        self.assertEqual(args.compression_level, 5)

        args = parser.parse_arguments(["--compression-level", "6"])
        self.assertEqual(args.compression_level, 6)

        args = parser.parse_arguments(["--compression-level", "7"])
        self.assertEqual(args.compression_level, 7)

        args = parser.parse_arguments(["--compression-level", "8"])
        self.assertEqual(args.compression_level, 8)

        args = parser.parse_arguments(["--compression-level", "9"])
        self.assertEqual(args.compression_level, 9)

        with redirect_stderr(io.StringIO()) as f, self.assertRaises(SystemExit):
            parser.parse_arguments(["--compression-level", "10"])

        self.assertIn(
            "error: argument --compression-level: invalid choice: 10 "
            "(choose from 0, 1, 2, 3, 4, 5, 6, 7, 8, 9)",
            f.getvalue(),
        )

    def test_gvmd_data_destination(self):
        parser = CliParser()
        args = parser.parse_arguments(["--gvmd-data-destination", "foo/bar"])
        self.assertEqual(args.gvmd_data_destination, Path("foo/bar"))

    def test_gvmd_data_url(self):
        parser = CliParser()
        args = parser.parse_arguments(
            ["--gvmd-data-url", "rsync://foo.bar/gvmd-data"]
        )
        self.assertEqual(args.gvmd_data_url, "rsync://foo.bar/gvmd-data")

    def test_notus_destination(self):
        parser = CliParser()
        args = parser.parse_arguments(["--notus-destination", "foo/bar"])
        self.assertEqual(args.notus_destination, Path("foo/bar"))

    def test_notus_url(self):
        parser = CliParser()
        args = parser.parse_arguments(["--notus-url", "rsync://foo.bar/notus"])
        self.assertEqual(args.notus_url, "rsync://foo.bar/notus")

    def test_nasl_destination(self):
        parser = CliParser()
        args = parser.parse_arguments(["--nasl-destination", "foo/bar"])
        self.assertEqual(args.nasl_destination, Path("foo/bar"))

    def test_nasl_url(self):
        parser = CliParser()
        args = parser.parse_arguments(["--nasl-url", "rsync://foo.bar/nasl"])
        self.assertEqual(args.nasl_url, "rsync://foo.bar/nasl")

    def test_scap_data_destination(self):
        parser = CliParser()
        args = parser.parse_arguments(["--scap-data-destination", "foo/bar"])
        self.assertEqual(args.scap_data_destination, Path("foo/bar"))

    def test_scap_data_url(self):
        parser = CliParser()
        args = parser.parse_arguments(
            ["--scap-data-url", "rsync://foo.bar/scap-data"]
        )
        self.assertEqual(args.scap_data_url, "rsync://foo.bar/scap-data")

    def test_cert_data_destination(self):
        parser = CliParser()
        args = parser.parse_arguments(["--cert-data-destination", "foo/bar"])
        self.assertEqual(args.cert_data_destination, Path("foo/bar"))

    def test_cert_data_url(self):
        parser = CliParser()
        args = parser.parse_arguments(
            ["--cert-data-url", "rsync://foo.bar/cert-data"]
        )
        self.assertEqual(args.cert_data_url, "rsync://foo.bar/cert-data")

    def test_report_formats_destination(self):
        parser = CliParser()
        args = parser.parse_arguments(
            ["--report-formats-destination", "foo/bar"]
        )
        self.assertEqual(args.report_formats_destination, Path("foo/bar"))

    def test_report_formats_url(self):
        parser = CliParser()
        args = parser.parse_arguments(
            ["--report-formats-url", "rsync://foo.bar/report-formats"]
        )
        self.assertEqual(
            args.report_formats_url, "rsync://foo.bar/report-formats"
        )

    def test_scan_configs_destination(self):
        parser = CliParser()
        args = parser.parse_arguments(["--scan-configs-destination", "foo/bar"])
        self.assertEqual(args.scan_configs_destination, Path("foo/bar"))

    def test_scan_configs_url(self):
        parser = CliParser()
        args = parser.parse_arguments(
            ["--scan-configs-url", "rsync://foo.bar/scan-configs"]
        )
        self.assertEqual(args.scan_configs_url, "rsync://foo.bar/scan-configs")

    def test_port_lists_destination(self):
        parser = CliParser()
        args = parser.parse_arguments(["--port-lists-destination", "foo/bar"])
        self.assertEqual(args.port_lists_destination, Path("foo/bar"))

    def test_port_lists_url(self):
        parser = CliParser()
        args = parser.parse_arguments(
            ["--port-lists-url", "rsync://foo.bar/port-lists"]
        )
        self.assertEqual(args.port_lists_url, "rsync://foo.bar/port-lists")

    def test_gvmd_lock_file(self):
        parser = CliParser()
        args = parser.parse_arguments(["--gvmd-lock-file", "/run/gvmd.lock"])
        self.assertEqual(args.gvmd_lock_file, Path("/run/gvmd.lock"))

    def test_openvas_lock_file(self):
        parser = CliParser()
        args = parser.parse_arguments(
            ["--openvas-lock-file", "/run/openvas.lock"]
        )
        self.assertEqual(args.openvas_lock_file, Path("/run/openvas.lock"))

    def test_fail_fast(self):
        parser = CliParser()
        args = parser.parse_arguments(["--fail-fast"])
        self.assertTrue(args.fail_fast)

        args = parser.parse_arguments(["--failfast"])
        self.assertTrue(args.fail_fast)

    def test_no_wait(self):
        parser = CliParser()
        args = parser.parse_arguments(["--no-wait"])
        self.assertTrue(args.no_wait)

    def test_wait_interval(self):
        parser = CliParser()
        args = parser.parse_arguments(["--wait-interval", "100"])
        self.assertEqual(args.wait_interval, 100)

    def test_rsync_timeout(self):
        parser = CliParser()
        args = parser.parse_arguments(["--rsync-timeout", "120"])
        self.assertEqual(args.rsync_timeout, 120)

    def test_other(self):
        parser = CliParser()

        with redirect_stderr(io.StringIO()) as f, self.assertRaises(
            SystemExit
        ) as cm:
            parser.parse_arguments(["--foo-bar", "10"])

        self.assertIn("error: unrecognized arguments: --foo-bar", f.getvalue())
        self.assertEqual(cm.exception.code, 2)

    @patch("greenbone.feed.sync.parser.Path")
    def test_config(self, path_mock: MagicMock):
        content = """[greenbone-feed-sync]
verbose = 3
feed-url = "rsync://foo.bar"
destination-prefix = "/usr/lib"
"""
        path_mock_instance = path_mock.return_value
        path_mock_instance.absolute.return_value = "/foo/bar/foo.toml"
        path_mock_instance.expanduser.return_value = path_mock_instance
        path_mock_instance.resolve.return_value = path_mock_instance
        path_mock_instance.exists.return_value = True
        path_mock_instance.read_text.return_value = content

        parser = CliParser()
        args = parser.parse_arguments(["--config", "foo.toml"])

        self.assertEqual(args.verbose, 3)
        self.assertEqual(args.feed_url, "rsync://foo.bar")
        self.assertEqual(args.destination_prefix, Path("/usr/lib"))

    @patch("greenbone.feed.sync.parser.Path")
    def test_load_from_default_config(self, path_mock: MagicMock):
        content = """[greenbone-feed-sync]
verbose = 3
feed-url = "rsync://foo.bar"
destination-prefix = "/usr/lib"
"""
        path_mock_instance = path_mock.return_value
        path_mock_instance.absolute.return_value = (
            "/foo/bar/.config/greenbone-feed-sync.toml"
        )
        path_mock_instance.expanduser.return_value = path_mock_instance
        path_mock_instance.resolve.return_value = path_mock_instance
        path_mock_instance.exists.return_value = True
        path_mock_instance.read_text.return_value = content

        parser = CliParser()
        args = parser.parse_arguments([])

        self.assertEqual(args.verbose, 3)
        self.assertEqual(args.feed_url, "rsync://foo.bar")
        self.assertEqual(args.destination_prefix, Path("/usr/lib"))

    @patch.dict(
        "os.environ",
        {
            "GREENBONE_FEED_SYNC_DESTINATION_PREFIX": "/usr/lib",
            "GREENBONE_FEED_SYNC_URL": "rsync://foo.bar",
            "GREENBONE_FEED_SYNC_VERBOSE": "3",
        },
    )
    def test_from_environment(self):
        parser = CliParser()
        args = parser.parse_arguments([])

        self.assertEqual(args.verbose, 3)
        self.assertEqual(args.feed_url, "rsync://foo.bar")
        self.assertEqual(args.destination_prefix, Path("/usr/lib"))

    @patch.dict(
        "os.environ",
        {
            "GREENBONE_FEED_SYNC_DESTINATION_PREFIX": "/usr/lib",
            "GREENBONE_FEED_SYNC_URL": "rsync://foo.bar",
            "GREENBONE_FEED_SYNC_VERBOSE": "3",
        },
    )
    @patch("greenbone.feed.sync.parser.Path")
    def test_environment_takes_precedence(self, path_mock):
        content = """[greenbone-feed-sync]
verbose = 9
feed-url = "rsync://lorem.ipsum"
destination-prefix = "/opt/lib"
wait-interval = 100
"""
        path_mock_instance = path_mock.return_value
        path_mock_instance.absolute.return_value = (
            "/foo/bar/.config/greenbone-feed-sync.toml"
        )
        path_mock_instance.expanduser.return_value = path_mock_instance
        path_mock_instance.resolve.return_value = path_mock_instance
        path_mock_instance.exists.return_value = True
        path_mock_instance.read_text.return_value = content

        parser = CliParser()
        args = parser.parse_arguments([])

        self.assertEqual(args.verbose, 3)
        self.assertEqual(args.feed_url, "rsync://foo.bar")
        self.assertEqual(args.destination_prefix, Path("/usr/lib"))
        self.assertEqual(args.wait_interval, 100)

    @patch.dict(
        "os.environ",
        {
            "GREENBONE_FEED_SYNC_DESTINATION_PREFIX": "/usr/lib",
            "GREENBONE_FEED_SYNC_URL": "rsync://foo.bar",
            "GREENBONE_FEED_SYNC_VERBOSE": "3",
        },
    )
    @patch("greenbone.feed.sync.parser.Path")
    def test_argument_takes_precedence(self, path_mock):
        content = """[greenbone-feed-sync]
verbose = 9
feed-url = "rsync://lorem.ipsum"
destination-prefix = "/opt/lib"
wait-interval = 100
"""
        path_mock_instance = path_mock.return_value
        path_mock_instance.absolute.return_value = (
            "/foo/bar/.config/greenbone-feed-sync.toml"
        )
        path_mock_instance.expanduser.return_value = path_mock_instance
        path_mock_instance.resolve.return_value = path_mock_instance
        path_mock_instance.exists.return_value = True
        path_mock_instance.read_text.return_value = content

        parser = CliParser()
        args = parser.parse_arguments(
            [
                "--wait-interval",
                "90",
            ]
        )

        self.assertEqual(args.verbose, 3)
        self.assertEqual(args.feed_url, "rsync://foo.bar")
        self.assertEqual(args.destination_prefix, Path("/usr/lib"))
        self.assertEqual(args.wait_interval, 90)

    def test_config_file_not_exists(self):
        parser = CliParser()

        with self.assertRaisesRegex(
            ConfigFileError, "Config file foo.bar does not exist."
        ):
            parser.parse_arguments(["--config", "foo.bar"])

    def test_type(self):
        parser = CliParser()
        args = parser.parse_arguments(["--type", "nvt"])
        self.assertEqual(args.type, "nvt")
        args = parser.parse_arguments(["--type", "nvts"])
        self.assertEqual(args.type, "nvt")
        args = parser.parse_arguments(["--type", "NVT"])
        self.assertEqual(args.type, "nvt")
        args = parser.parse_arguments(["--type", "NVTS"])
        self.assertEqual(args.type, "nvt")

        args = parser.parse_arguments(["--type", "notus"])
        self.assertEqual(args.type, "notus")
        args = parser.parse_arguments(["--type", "NOTUS"])
        self.assertEqual(args.type, "notus")
        args = parser.parse_arguments(["--type", "NoTuS"])
        self.assertEqual(args.type, "notus")

        args = parser.parse_arguments(["--type", "nasl"])
        self.assertEqual(args.type, "nasl")
        args = parser.parse_arguments(["--type", "NASL"])
        self.assertEqual(args.type, "nasl")
        args = parser.parse_arguments(["--type", "NaSl"])
        self.assertEqual(args.type, "nasl")

        args = parser.parse_arguments(["--type", "scap"])
        self.assertEqual(args.type, "scap")
        args = parser.parse_arguments(["--type", "SCAP"])
        self.assertEqual(args.type, "scap")
        args = parser.parse_arguments(["--type", "ScAp"])
        self.assertEqual(args.type, "scap")

        args = parser.parse_arguments(["--type", "cert"])
        self.assertEqual(args.type, "cert")
        args = parser.parse_arguments(["--type", "CERT"])
        self.assertEqual(args.type, "cert")
        args = parser.parse_arguments(["--type", "CeRt"])
        self.assertEqual(args.type, "cert")

        args = parser.parse_arguments(["--type", "all"])
        self.assertEqual(args.type, "all")
        args = parser.parse_arguments(["--type", "ALL"])
        self.assertEqual(args.type, "all")
        args = parser.parse_arguments(["--type", "AlL"])
        self.assertEqual(args.type, "all")

        args = parser.parse_arguments(["--type", "report-format"])
        self.assertEqual(args.type, "report-format")
        args = parser.parse_arguments(["--type", "REPORT-FORMAT"])
        self.assertEqual(args.type, "report-format")
        args = parser.parse_arguments(["--type", "report_format"])
        self.assertEqual(args.type, "report-format")
        args = parser.parse_arguments(["--type", "REPORT_FORMAT"])
        self.assertEqual(args.type, "report-format")
        args = parser.parse_arguments(["--type", "Report-Format"])
        self.assertEqual(args.type, "report-format")
        args = parser.parse_arguments(["--type", "report-formats"])
        self.assertEqual(args.type, "report-format")
        args = parser.parse_arguments(["--type", "REPORT_FORMATS"])
        self.assertEqual(args.type, "report-format")

        args = parser.parse_arguments(["--type", "scan-config"])
        self.assertEqual(args.type, "scan-config")
        args = parser.parse_arguments(["--type", "SCAN-CONFIG"])
        self.assertEqual(args.type, "scan-config")
        args = parser.parse_arguments(["--type", "scan_config"])
        self.assertEqual(args.type, "scan-config")
        args = parser.parse_arguments(["--type", "SCAN_config"])
        self.assertEqual(args.type, "scan-config")
        args = parser.parse_arguments(["--type", "Scan-Config"])
        self.assertEqual(args.type, "scan-config")
        args = parser.parse_arguments(["--type", "scan-configs"])
        self.assertEqual(args.type, "scan-config")
        args = parser.parse_arguments(["--type", "SCAN_CONFIGS"])
        self.assertEqual(args.type, "scan-config")

        args = parser.parse_arguments(["--type", "port-list"])
        self.assertEqual(args.type, "port-list")
        args = parser.parse_arguments(["--type", "PORT-LIST"])
        self.assertEqual(args.type, "port-list")
        args = parser.parse_arguments(["--type", "port_list"])
        self.assertEqual(args.type, "port-list")
        args = parser.parse_arguments(["--type", "PORT_LIST"])
        self.assertEqual(args.type, "port-list")
        args = parser.parse_arguments(["--type", "port-list"])
        self.assertEqual(args.type, "port-list")
        args = parser.parse_arguments(["--type", "port-lists"])
        self.assertEqual(args.type, "port-list")
        args = parser.parse_arguments(["--type", "PORT_LISTS"])
        self.assertEqual(args.type, "port-list")

        args = parser.parse_arguments(["--type", "gvmd-data"])
        self.assertEqual(args.type, "gvmd-data")
        args = parser.parse_arguments(["--type", "GVMD-DATA"])
        self.assertEqual(args.type, "gvmd-data")
        args = parser.parse_arguments(["--type", "gvmd_data"])
        self.assertEqual(args.type, "gvmd-data")
        args = parser.parse_arguments(["--type", "GVMD_DATA"])
        self.assertEqual(args.type, "gvmd-data")
        args = parser.parse_arguments(["--type", "gvmd-data"])
        self.assertEqual(args.type, "gvmd-data")

    def test_group(self):
        parser = CliParser()
        args = parser.parse_arguments(["--group", "some_group"])
        self.assertEqual(args.group, "some_group")

        args = parser.parse_arguments(["--group", "123"])
        self.assertEqual(args.group, 123)

    def test_user(self):
        parser = CliParser()
        args = parser.parse_arguments(["--user", "some_user"])
        self.assertEqual(args.user, "some_user")

        args = parser.parse_arguments(["--user", "123"])
        self.assertEqual(args.user, 123)
