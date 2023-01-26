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

import asyncio
import unittest
from asyncio.subprocess import Process
from unittest.mock import AsyncMock, patch

from greenbone.feed.sync.errors import RsyncError
from greenbone.feed.sync.rsync import Rsync, exec_rsync


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


class ExecRsyncTestCase(unittest.IsolatedAsyncioTestCase):
    @patch(
        "greenbone.feed.sync.rsync.asyncio.create_subprocess_exec",
        autospec=True,
    )
    async def test_failure(self, exec_mock: AsyncMock):
        process_mock = AsyncMock(spec=Process)
        process_mock.communicate.return_value = (None, b"An error occurred")
        process_mock.wait.return_value = 1
        exec_mock.return_value = process_mock

        with self.assertRaises(RsyncError) as cm:
            await exec_rsync("foo", "bar")

        exec_mock.assert_awaited_once_with(
            "rsync", "foo", "bar", stderr=asyncio.subprocess.PIPE
        )

        self.assertEqual(cm.exception.returncode, 1)
        self.assertEqual(cm.exception.stderr, "An error occurred")
        self.assertEqual(cm.exception.cmd, ["rsync", "foo", "bar"])
        self.assertIsNone(cm.exception.stout)
        self.assertEqual(
            str(cm.exception),
            "'rsync foo bar' returned non-zero exit status 1.",
        )

    @patch(
        "greenbone.feed.sync.rsync.asyncio.create_subprocess_exec",
        autospec=True,
    )
    async def test_success(self, exec_mock: AsyncMock):
        process_mock = AsyncMock(spec=Process)
        process_mock.communicate.return_value = (None, None)
        process_mock.wait.return_value = 0
        exec_mock.return_value = process_mock

        await exec_rsync("foo", "bar")

        exec_mock.assert_awaited_once_with(
            "rsync", "foo", "bar", stderr=asyncio.subprocess.PIPE
        )

    @patch("greenbone.feed.sync.rsync.exec_rsync", autospec=True)
    async def test_rsync_with_timeout(self, exec_mock: AsyncMock):
        rsync = Rsync(timeout=120)
        await rsync.sync("rsync://foo.bar/baz", "/tmp/baz")

        exec_mock.assert_awaited_once_with(
            "--links",
            "--times",
            "--omit-dir-times",
            "--recursive",
            "--partial",
            "--progress",
            "--timeout=120",
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
