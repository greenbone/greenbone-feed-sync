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
from unittest.mock import AsyncMock, patch

from greenbone.feed.sync.rsync import Rsync


class RsyncTestCase(unittest.IsolatedAsyncioTestCase):
    @patch("greenbone.feed.sync.rsync.exec_rsync", autospec=True)
    async def test_rsync_with_defaults(self, exec_mock: AsyncMock):
        rsync = Rsync()
        await rsync.sync("rsync://foo.bar/baz", "/tmp/baz")

        exec_mock.assert_awaited_once_with(
            "--links",
            "--times",
            "--omit-dir-times",
            "--recursive",
            "--partial",
            "--progress",
            "-q",
            "--compress-level=9",
            "--delete",
            "--perms",
            "--chmod=Fugo+r,Fug+w,Dugo-s,Dugo+rx,Dug+w",
            "--copy-unsafe-links",
            "--hard-links",
            "rsync://foo.bar/baz",
            "/tmp/baz",
        )

    @patch("greenbone.feed.sync.rsync.exec_rsync", autospec=True)
    async def test_rsync_with_private_subdir(self, exec_mock: AsyncMock):
        rsync = Rsync(private_subdir="private")
        await rsync.sync("rsync://foo.bar/baz", "/tmp/baz")

        exec_mock.assert_awaited_once_with(
            "--links",
            "--times",
            "--omit-dir-times",
            "--recursive",
            "--partial",
            "--progress",
            "-q",
            "--compress-level=9",
            "--delete",
            "--exclude",
            "private",
            "--perms",
            "--chmod=Fugo+r,Fug+w,Dugo-s,Dugo+rx,Dug+w",
            "--copy-unsafe-links",
            "--hard-links",
            "rsync://foo.bar/baz",
            "/tmp/baz",
        )

    @patch("greenbone.feed.sync.rsync.exec_rsync", autospec=True)
    async def test_rsync_with_verbose(self, exec_mock: AsyncMock):
        rsync = Rsync(verbose=True)
        await rsync.sync("rsync://foo.bar/baz", "/tmp/baz")

        exec_mock.assert_awaited_once_with(
            "--links",
            "--times",
            "--omit-dir-times",
            "--recursive",
            "--partial",
            "--progress",
            "-v",
            "--compress-level=9",
            "--delete",
            "--perms",
            "--chmod=Fugo+r,Fug+w,Dugo-s,Dugo+rx,Dug+w",
            "--copy-unsafe-links",
            "--hard-links",
            "rsync://foo.bar/baz",
            "/tmp/baz",
        )

    @patch("greenbone.feed.sync.rsync.exec_rsync", autospec=True)
    async def test_rsync_with_compression_level(self, exec_mock: AsyncMock):
        rsync = Rsync(compression_level=1)
        await rsync.sync("rsync://foo.bar/baz", "/tmp/baz")

        exec_mock.assert_awaited_once_with(
            "--links",
            "--times",
            "--omit-dir-times",
            "--recursive",
            "--partial",
            "--progress",
            "-q",
            "--compress-level=1",
            "--delete",
            "--perms",
            "--chmod=Fugo+r,Fug+w,Dugo-s,Dugo+rx,Dug+w",
            "--copy-unsafe-links",
            "--hard-links",
            "rsync://foo.bar/baz",
            "/tmp/baz",
        )
