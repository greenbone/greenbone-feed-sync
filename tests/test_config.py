# SPDX-FileCopyrightText: 2023-2024 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

# pylint: disable=line-too-long
# ruff: noqa: E501

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from pontos.testing import temp_file

from greenbone.feed.sync.config import (
    DEFAULT_DESTINATION_PREFIX,
    DEFAULT_ENTERPRISE_KEY_PATH,
    DEFAULT_FEED_RELEASE,
    DEFAULT_GROUP,
    DEFAULT_GVMD_LOCK_FILE_PATH,
    DEFAULT_OPENVAS_LOCK_FILE_PATH,
    DEFAULT_USER,
    Config,
    EnterpriseSettings,
)
from greenbone.feed.sync.errors import ConfigError, ConfigFileError
from greenbone.feed.sync.helper import DEFAULT_FLOCK_WAIT_INTERVAL
from greenbone.feed.sync.rsync import (
    DEFAULT_RSYNC_COMPRESSION_LEVEL,
    DEFAULT_RSYNC_URL,
)


class ConfigTestCase(unittest.TestCase):
    def test_defaults(self):
        values = Config.load()

        self.assertEqual(len(values), 31)
        self.assertEqual(
            values["destination-prefix"], Path(DEFAULT_DESTINATION_PREFIX)
        )
        self.assertEqual(
            values["gvmd-data-destination"],
            Path(DEFAULT_DESTINATION_PREFIX) / "gvm" / "data-objects" / "gvmd",
        )
        self.assertEqual(
            values["gvmd-data-url"],
            f"{DEFAULT_RSYNC_URL}/data-feed/{DEFAULT_FEED_RELEASE}/",
        )
        self.assertEqual(values["feed-url"], DEFAULT_RSYNC_URL)
        self.assertEqual(
            values["notus-destination"],
            Path(DEFAULT_DESTINATION_PREFIX) / "notus",
        )
        self.assertEqual(
            values["notus-url"],
            f"{DEFAULT_RSYNC_URL}/vulnerability-feed/{DEFAULT_FEED_RELEASE}/vt-data/notus/",
        )
        self.assertEqual(
            values["nasl-destination"],
            Path(DEFAULT_DESTINATION_PREFIX) / "openvas" / "plugins",
        )
        self.assertEqual(
            values["nasl-url"],
            f"{DEFAULT_RSYNC_URL}/vulnerability-feed/{DEFAULT_FEED_RELEASE}/vt-data/nasl/",
        )
        self.assertEqual(
            values["scap-data-destination"],
            Path(DEFAULT_DESTINATION_PREFIX) / "gvm" / "scap-data",
        )
        self.assertEqual(
            values["scap-data-url"],
            f"{DEFAULT_RSYNC_URL}/vulnerability-feed/{DEFAULT_FEED_RELEASE}/scap-data/",
        )
        self.assertEqual(
            values["cert-data-destination"],
            Path(DEFAULT_DESTINATION_PREFIX) / "gvm" / "cert-data",
        )
        self.assertEqual(
            values["cert-data-url"],
            f"{DEFAULT_RSYNC_URL}/vulnerability-feed/{DEFAULT_FEED_RELEASE}/cert-data/",
        )
        self.assertEqual(
            values["report-formats-destination"],
            Path(DEFAULT_DESTINATION_PREFIX)
            / "gvm"
            / "data-objects"
            / "gvmd"
            / "report-formats",
        )
        self.assertEqual(
            values["report-formats-url"],
            f"{DEFAULT_RSYNC_URL}/data-feed/{DEFAULT_FEED_RELEASE}/report-formats/",
        )
        self.assertEqual(
            values["scan-configs-destination"],
            Path(DEFAULT_DESTINATION_PREFIX)
            / "gvm"
            / "data-objects"
            / "gvmd"
            / "scan-configs",
        )
        self.assertEqual(
            values["scan-configs-url"],
            f"{DEFAULT_RSYNC_URL}/data-feed/{DEFAULT_FEED_RELEASE}/scan-configs/",
        )
        self.assertEqual(
            values["port-lists-destination"],
            Path(DEFAULT_DESTINATION_PREFIX)
            / "gvm"
            / "data-objects"
            / "gvmd"
            / "port-lists",
        )
        self.assertEqual(
            values["port-lists-url"],
            f"{DEFAULT_RSYNC_URL}/data-feed/{DEFAULT_FEED_RELEASE}/port-lists/",
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
        self.assertEqual(
            values["greenbone-enterprise-feed-key"],
            Path(DEFAULT_ENTERPRISE_KEY_PATH),
        )
        self.assertEqual(values["feed-release"], DEFAULT_FEED_RELEASE)

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
greenbone-enterprise-feed-key = "/srv/feed.key"
feed-release = "1.2.3"
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
        self.assertEqual(
            values["greenbone-enterprise-feed-key"], Path("/srv/feed.key")
        )
        self.assertEqual(values["feed-release"], "1.2.3")

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
            Path("/opt/lib/gvm/data-objects/gvmd/"),
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
            Path("/opt/lib/gvm/data-objects/gvmd/report-formats"),
        )
        self.assertEqual(
            values["scan-configs-destination"],
            Path("/opt/lib/gvm/data-objects/gvmd/scan-configs"),
        )
        self.assertEqual(
            values["port-lists-destination"],
            Path("/opt/lib/gvm/data-objects/gvmd/port-lists"),
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
            f"rsync://foo.bar/data-feed/{DEFAULT_FEED_RELEASE}/",
        )
        self.assertEqual(
            values["notus-url"],
            f"rsync://foo.bar/vulnerability-feed/{DEFAULT_FEED_RELEASE}/vt-data/notus/",
        )
        self.assertEqual(
            values["nasl-url"],
            f"rsync://foo.bar/vulnerability-feed/{DEFAULT_FEED_RELEASE}/vt-data/nasl/",
        )
        self.assertEqual(
            values["scap-data-url"],
            f"rsync://foo.bar/vulnerability-feed/{DEFAULT_FEED_RELEASE}/scap-data/",
        )
        self.assertEqual(
            values["cert-data-url"],
            f"rsync://foo.bar/vulnerability-feed/{DEFAULT_FEED_RELEASE}/cert-data/",
        )
        self.assertEqual(
            values["report-formats-url"],
            f"rsync://foo.bar/data-feed/{DEFAULT_FEED_RELEASE}/report-formats/",
        )
        self.assertEqual(
            values["scan-configs-url"],
            f"rsync://foo.bar/data-feed/{DEFAULT_FEED_RELEASE}/scan-configs/",
        )
        self.assertEqual(
            values["port-lists-url"],
            f"rsync://foo.bar/data-feed/{DEFAULT_FEED_RELEASE}/port-lists/",
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
            "GREENBONE_FEED_SYNC_ENTERPRISE_FEED_KEY": "/tmp/some.key",
            "GREENBONE_FEED_SYNC_FEED_RELEASE": "1.2.3",
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
        self.assertEqual(
            values["greenbone-enterprise-feed-key"], Path("/tmp/some.key")
        )
        self.assertEqual(values["feed-release"], "1.2.3")

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
            "GREENBONE_FEED_SYNC_ENTERPRISE_FEED_KEY": "/tmp/some.key",
            "GREENBONE_FEED_SYNC_FEED_RELEASE": "1.2.3",
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
greenbone-enterprise-feed-key = "/srv/feed.key"
feed-release = "2.3.4"
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
        self.assertEqual(
            values["greenbone-enterprise-feed-key"], Path("/tmp/some.key")
        )
        self.assertEqual(values["feed-release"], "1.2.3")

    def test_feed_release(self):
        feed_release = "1.2.3"
        content = f"""[greenbone-feed-sync]
feed-release = "{feed_release}"
"""
        path_mock = MagicMock(spec=Path)
        path_mock.read_text.return_value = content

        values = Config.load(path_mock)

        self.assertEqual(
            values["gvmd-data-destination"],
            Path(DEFAULT_DESTINATION_PREFIX)
            / "gvm"
            / "data-objects"
            / "gvmd"
            / feed_release,
        )
        self.assertEqual(
            values["gvmd-data-url"],
            f"{DEFAULT_RSYNC_URL}/data-feed/{feed_release}/",
        )
        self.assertEqual(values["feed-url"], DEFAULT_RSYNC_URL)
        self.assertEqual(
            values["notus-destination"],
            Path(DEFAULT_DESTINATION_PREFIX) / "notus",
        )
        self.assertEqual(
            values["notus-url"],
            f"{DEFAULT_RSYNC_URL}/vulnerability-feed/{feed_release}/vt-data/notus/",
        )
        self.assertEqual(
            values["nasl-destination"],
            Path(DEFAULT_DESTINATION_PREFIX) / "openvas" / "plugins",
        )
        self.assertEqual(
            values["nasl-url"],
            f"{DEFAULT_RSYNC_URL}/vulnerability-feed/{feed_release}/vt-data/nasl/",
        )
        self.assertEqual(
            values["scap-data-destination"],
            Path(DEFAULT_DESTINATION_PREFIX) / "gvm" / "scap-data",
        )
        self.assertEqual(
            values["scap-data-url"],
            f"{DEFAULT_RSYNC_URL}/vulnerability-feed/{feed_release}/scap-data/",
        )
        self.assertEqual(
            values["cert-data-destination"],
            Path(DEFAULT_DESTINATION_PREFIX) / "gvm" / "cert-data",
        )
        self.assertEqual(
            values["cert-data-url"],
            f"{DEFAULT_RSYNC_URL}/vulnerability-feed/{feed_release}/cert-data/",
        )
        self.assertEqual(
            values["report-formats-destination"],
            Path(DEFAULT_DESTINATION_PREFIX)
            / "gvm"
            / "data-objects"
            / "gvmd"
            / feed_release
            / "report-formats",
        )
        self.assertEqual(
            values["report-formats-url"],
            f"{DEFAULT_RSYNC_URL}/data-feed/{feed_release}/report-formats/",
        )
        self.assertEqual(
            values["scan-configs-destination"],
            Path(DEFAULT_DESTINATION_PREFIX)
            / "gvm"
            / "data-objects"
            / "gvmd"
            / feed_release
            / "scan-configs",
        )
        self.assertEqual(
            values["scan-configs-url"],
            f"{DEFAULT_RSYNC_URL}/data-feed/{feed_release}/scan-configs/",
        )
        self.assertEqual(
            values["port-lists-destination"],
            Path(DEFAULT_DESTINATION_PREFIX)
            / "gvm"
            / "data-objects"
            / "gvmd"
            / feed_release
            / "port-lists",
        )
        self.assertEqual(
            values["port-lists-url"],
            f"{DEFAULT_RSYNC_URL}/data-feed/{feed_release}/port-lists/",
        )

    def test_invalid_feed_release(self):
        feed_release = "abc"
        content = f"""[greenbone-feed-sync]
feed-release = "{feed_release}"
"""
        path_mock = MagicMock(spec=Path)
        path_mock.read_text.return_value = content

        with self.assertRaisesRegex(
            ConfigError, "Invalid feed release format: abc"
        ):
            Config.load(path_mock)

        feed_release = "a.b"
        content = f"""[greenbone-feed-sync]
feed-release = "{feed_release}"
"""
        path_mock = MagicMock(spec=Path)
        path_mock.read_text.return_value = content

        with self.assertRaisesRegex(
            ConfigError, "Invalid feed release format: a.b"
        ):
            Config.load(path_mock)

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

    def test_getitem(self):
        content = """[greenbone-feed-sync]
no-wait = false
compression-level = 7
private-directory = "private"
"""
        path_mock = MagicMock(spec=Path)
        path_mock.read_text.return_value = content

        values = Config.load(path_mock)

        self.assertFalse(values["no-wait"])
        self.assertEqual(values["compression-level"], 7)
        self.assertEqual(values["private-directory"], Path("private"))

    def test_setitem(self):
        config = Config()

        config["no-wait"] = True
        config["compression-level"] = 7
        config["private-directory"] = "private"

        self.assertTrue(config["no-wait"])
        self.assertEqual(config["compression-level"], 7)
        self.assertEqual(config["private-directory"], "private")


class EnterpriseSettingsTestCase(unittest.TestCase):
    def test_from_key(self):
        content = """a_user@some.feed.server:/feed/
Lorem ipsum dolor sit amet,
consetetur sadipscing elitr,
sed diam nonumy eirmod tempor
"""
        with temp_file(content=content, name="enterprise.key") as f:
            settings = EnterpriseSettings.from_key(f)

            self.assertEqual(settings.key, f)
            self.assertEqual(settings.host, "some.feed.server")
            self.assertEqual(settings.user, "a_user")

    def test_feed_url(self):
        key = Path("/tmp/some.key")
        settings = EnterpriseSettings("foo", "some.server", key)

        self.assertEqual(
            settings.feed_url(), "ssh://foo@some.server/enterprise"
        )
