# SPDX-FileCopyrightText: 2023-2024 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import asyncio
import unittest
from asyncio.subprocess import Process
from pathlib import Path
from unittest.mock import AsyncMock, patch

from pontos.testing import temp_directory

from greenbone.feed.sync.errors import RsyncError
from greenbone.feed.sync.rsync import Rsync, exec_rsync


class RsyncTestCase(unittest.IsolatedAsyncioTestCase):
    @patch("greenbone.feed.sync.rsync.exec_rsync", autospec=True)
    async def test_rsync_with_custom_ssh_port(self, exec_mock: AsyncMock):
        with temp_directory() as temp_dir:
            await Rsync(ssh_key=Path("/tmp/ssh.key")).sync(
                "ssh://user@host:2222/feed", temp_dir
            )

        exec_mock.assert_awaited_once()
        args = exec_mock.await_args.args
        self.assertEqual(
            args[args.index("-e") + 1],
            "ssh -o UserKnownHostsFile=/dev/null "
            "-o StrictHostKeyChecking=no -p 2222 -i '/tmp/ssh.key'",
        )
        self.assertEqual(args[-2], "user@host:/feed")

    @patch("greenbone.feed.sync.rsync.exec_rsync", autospec=True)
    async def test_creates_destination_before_sync(self, exec_mock: AsyncMock):
        with temp_directory() as temp_dir:
            destination = temp_dir / "nested" / "feed"

            async def check_destination(*args):
                self.assertTrue(destination.is_dir())
                self.assertEqual(args[-1], str(destination.absolute()))

            exec_mock.side_effect = check_destination
            await Rsync().sync("rsync://foo.bar/baz", destination)

            exec_mock.assert_awaited_once()

    @patch("greenbone.feed.sync.rsync.exec_rsync", autospec=True)
    async def test_destination_creation_failure(self, exec_mock: AsyncMock):
        with temp_directory() as temp_dir:
            destination = temp_dir / "feed"
            destination.touch()

            with self.assertRaises(FileExistsError):
                await Rsync().sync("rsync://foo.bar/baz", destination)

            exec_mock.assert_not_awaited()

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

    @patch("greenbone.feed.sync.rsync.exec_rsync", autospec=True)
    async def test_rsync_timeout_zero_and_none(self, exec_mock: AsyncMock):
        for timeout in (0, None):
            with self.subTest(timeout=timeout):
                exec_mock.reset_mock()
                await Rsync(timeout=timeout).sync(
                    "rsync://foo.bar/baz", "/tmp/baz"
                )

                exec_mock.assert_awaited_once()
                timeout_args = [
                    arg
                    for arg in exec_mock.await_args.args
                    if arg.startswith("--timeout=")
                ]
                self.assertEqual(
                    timeout_args, ["--timeout=0"] if timeout == 0 else []
                )

    @patch("greenbone.feed.sync.rsync.exec_rsync", autospec=True)
    async def test_rsync_compression_zero_and_none(self, exec_mock: AsyncMock):
        for compression_level in (0, None):
            with self.subTest(compression_level=compression_level):
                exec_mock.reset_mock()
                await Rsync(compression_level=compression_level).sync(
                    "rsync://foo.bar/baz", "/tmp/baz"
                )

                exec_mock.assert_awaited_once()
                compression_args = [
                    arg
                    for arg in exec_mock.await_args.args
                    if arg.startswith("--compress-level=")
                ]
                self.assertEqual(
                    compression_args,
                    ["--compress-level=0"] if compression_level == 0 else [],
                )

    @patch("greenbone.feed.sync.rsync.exec_rsync", autospec=True)
    async def test_rsync_with_no_permission_change(self, exec_mock: AsyncMock):
        rsync = Rsync(change_permissions=False)
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
            "--no-perms",
            "--copy-unsafe-links",
            "--hard-links",
            "rsync://foo.bar/baz",
            "/tmp/baz",
        )

        args = exec_mock.await_args.args
        self.assertNotIn("--perms", args)
        self.assertFalse(
            any(arg.startswith("--chmod") for arg in args),
        )

    @patch("greenbone.feed.sync.rsync.exec_rsync", autospec=True)
    async def test_rsync_with_exclude(self, exec_mock: AsyncMock):
        rsync = Rsync(exclude=["foo", Path("exclude/this")])
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
            "foo",
            "--exclude",
            "exclude/this",
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

    @patch("greenbone.feed.sync.rsync.exec_rsync", autospec=True)
    async def test_rsync_with_ssh(self, exec_mock: AsyncMock):
        ssh_key = Path("/tmp/ssh.key")
        rsync = Rsync(ssh_key=ssh_key)
        await rsync.sync("ssh://user@foo.bar/baz", "/tmp/baz")

        exec_mock.assert_awaited_once_with(
            "--links",
            "--times",
            "--omit-dir-times",
            "--recursive",
            "--partial",
            "--progress",
            "-e",
            "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -p 24 -i '/tmp/ssh.key'",  # pylint: disable=line-too-long
            "-q",
            "--compress-level=9",
            "--delete",
            "--perms",
            "--chmod=Fugo+r,Fug+w,Dugo-s,Dugo+rx,Dug+w",
            "--copy-unsafe-links",
            "--hard-links",
            "user@foo.bar:/baz",
            "/tmp/baz",
        )
