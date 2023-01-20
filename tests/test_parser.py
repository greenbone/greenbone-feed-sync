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

# pylint: disable=line-too-long

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from greenbone.feed.sync.helper import DEFAULT_FLOCK_WAIT_INTERVAL
from greenbone.feed.sync.parser import (
    DEFAULT_CERT_DATA_PATH,
    DEFAULT_CERT_DATA_URL_PATH,
    DEFAULT_DESTINATION_PREFIX,
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


class ConfigTestCase(unittest.TestCase):
    def test_defaults(self):
        values = Config.load()

        self.assertEqual(len(values), 24)
        self.assertEqual(
            values["destination-prefix"], Path(DEFAULT_DESTINATION_PREFIX)
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

    def test_config_file(self):
        content = """[greenbone-feed-sync]
destination-prefix = "/opt/lib"
feed-url = "rsync://lorem.ipsum"
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
"""
        path_mock = MagicMock(spec=Path)
        path_mock.read_text.return_value = content

        values = Config.load(path_mock)

        self.assertEqual(values["destination-prefix"], Path("/opt/lib"))
        self.assertEqual(values["feed-url"], "rsync://lorem.ipsum")
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

    def test_destination_prefix(self):
        content = """[greenbone-feed-sync]
destination-prefix = "/opt/lib/"
"""

        path_mock = MagicMock(spec=Path)
        path_mock.read_text.return_value = content

        values = Config.load(path_mock)

        self.assertEqual(values["destination-prefix"], Path("/opt/lib"))
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
            "GREENBONE_FEED_SYNC_NOTUS_DESTINATION": "/usr/lib/notus",
            "GREENBONE_FEED_SYNC_NOTUS_URL": "rsync://foo.bar/notus",
            "GREENBONE_NASL_DESTINATION": "/usr/lib/openvas/plugins/",
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
        },
    )
    def test_environment(self):
        values = Config.load()

        self.assertEqual(values["destination-prefix"], Path("/opt/lib"))
        self.assertEqual(values["feed-url"], "rsync://lorem.ipsum")
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

    @patch.dict(
        "os.environ",
        {
            "GREENBONE_FEED_SYNC_DESTINATION_PREFIX": "/opt/lib",
            "GREENBONE_FEED_SYNC_URL": "rsync://lorem.ipsum",
            "GREENBONE_FEED_SYNC_NOTUS_DESTINATION": "/usr/lib/notus",
            "GREENBONE_FEED_SYNC_NOTUS_URL": "rsync://foo.bar/notus",
            "GREENBONE_NASL_DESTINATION": "/usr/lib/openvas/plugins/",
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
        },
    )
    def test_environment_overrides_config_file(self):
        content = """[greenbone-feed-sync]
destination-prefix = "/svr/lib"
feed-url = "rsync://ipsum.lorem"
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
"""
        path_mock = MagicMock(spec=Path)
        path_mock.read_text.return_value = content

        values = Config.load(path_mock)

        self.assertEqual(values["destination-prefix"], Path("/opt/lib"))
        self.assertEqual(values["feed-url"], "rsync://lorem.ipsum")
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
