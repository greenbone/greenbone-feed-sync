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

import unittest

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
        values = Config().load()

        self.assertEqual(len(values), 24)
        self.assertEqual(
            values["destination-prefix"], DEFAULT_DESTINATION_PREFIX
        )
        self.assertEqual(values["feed-url"], DEFAULT_RSYNC_URL)
        self.assertEqual(
            values["notus-destination"],
            f"{DEFAULT_DESTINATION_PREFIX}{DEFAULT_NOTUS_PATH}",
        )
        self.assertEqual(
            values["notus-url"], f"{DEFAULT_RSYNC_URL}{DEFAULT_NOTUS_URL_PATH}"
        )
        self.assertEqual(
            values["nasl-destination"],
            f"{DEFAULT_DESTINATION_PREFIX}{DEFAULT_NASL_PATH}",
        )
        self.assertEqual(
            values["nasl-url"], f"{DEFAULT_RSYNC_URL}{DEFAULT_NASL_URL_PATH}"
        )
        self.assertEqual(
            values["scap-data-destination"],
            f"{DEFAULT_DESTINATION_PREFIX}{DEFAULT_SCAP_DATA_PATH}",
        )
        self.assertEqual(
            values["scap-data-url"],
            f"{DEFAULT_RSYNC_URL}{DEFAULT_SCAP_DATA_URL_PATH}",
        )
        self.assertEqual(
            values["cert-data-destination"],
            f"{DEFAULT_DESTINATION_PREFIX}{DEFAULT_CERT_DATA_PATH}",
        )
        self.assertEqual(
            values["cert-data-url"],
            f"{DEFAULT_RSYNC_URL}{DEFAULT_CERT_DATA_URL_PATH}",
        )
        self.assertEqual(
            values["report-formats-destination"],
            f"{DEFAULT_DESTINATION_PREFIX}{DEFAULT_REPORT_FORMATS_PATH}",
        )
        self.assertEqual(
            values["report-formats-url"],
            f"{DEFAULT_RSYNC_URL}{DEFAULT_REPORT_FORMATS_URL_PATH}",
        )
        self.assertEqual(
            values["scan-configs-destination"],
            f"{DEFAULT_DESTINATION_PREFIX}{DEFAULT_SCAN_CONFIGS_PATH}",
        )
        self.assertEqual(
            values["scan-configs-url"],
            f"{DEFAULT_RSYNC_URL}{DEFAULT_SCAN_CONFIGS_URL_PATH}",
        )
        self.assertEqual(
            values["port-lists-destination"],
            f"{DEFAULT_DESTINATION_PREFIX}{DEFAULT_PORT_LISTS_PATH}",
        )
        self.assertEqual(
            values["port-lists-url"],
            f"{DEFAULT_RSYNC_URL}{DEFAULT_PORT_LISTS_URL_PATH}",
        )
        self.assertEqual(
            values["gvmd-lock-file"],
            f"{DEFAULT_DESTINATION_PREFIX}{DEFAULT_GVMD_LOCK_FILE_PATH}",
        )
        self.assertEqual(
            values["openvas-lock-file"],
            f"{DEFAULT_DESTINATION_PREFIX}{DEFAULT_OPENVAS_LOCK_FILE_PATH}",
        )
        self.assertEqual(values["wait-interval"], DEFAULT_FLOCK_WAIT_INTERVAL)
        self.assertFalse(values["no-wait"])
        self.assertEqual(
            values["compression-level"], DEFAULT_RSYNC_COMPRESSION_LEVEL
        )
        self.assertIsNone(values["private-directory"])
        self.assertIsNone(values["verbose"])
        self.assertFalse(values["fail-fast"])
