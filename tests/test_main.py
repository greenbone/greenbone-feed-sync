# SPDX-FileCopyrightText: 2023-2024 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from pontos.testing import temp_directory

from greenbone.feed.sync.config import DEFAULT_FEED_RELEASE
from greenbone.feed.sync.errors import GreenboneFeedSyncError, RsyncError
from greenbone.feed.sync.main import (
    Sync,
    do_selftest,
    feed_sync,
    filter_syncs,
    main,
)


class FilterSyncsTestCase(unittest.TestCase):
    def test_filter_syncs(self):
        sync_a = Sync(name="a", types=["foo", "bar"], url="a", destination="a")
        sync_b = Sync(name="b", types=["foo", "baz"], url="b", destination="b")
        sync_c = Sync(name="c", types=["bar", "baz"], url="c", destination="c")

        sync_list = filter_syncs(
            "file.lock",
            "foo",
            sync_a,
            sync_b,
            sync_c,
        )

        self.assertEqual(len(sync_list.syncs), 2)
        self.assertEqual(sync_list.lock_file, "file.lock")

        self.assertEqual(sync_list.syncs[0], sync_a)
        self.assertEqual(sync_list.syncs[1], sync_b)


class DoSelftestTestCase(unittest.TestCase):
    @patch("greenbone.feed.sync.main.subprocess.run", autospec=True)
    def test_do_selftest_missing_or_failing_binary(
        self, mock_subprocess_run: MagicMock
    ):
        for error in (
            FileNotFoundError("rsync not found"),
            subprocess.CalledProcessError(1, ["rsync", "--help"]),
        ):
            with self.subTest(error=type(error).__name__):
                mock_subprocess_run.side_effect = error
                with self.assertRaisesRegex(
                    GreenboneFeedSyncError,
                    "The rsync binary could not be found.",
                ):
                    do_selftest()

    @patch("greenbone.feed.sync.main.subprocess.run")
    def test_do_selftest_success(self, mock_subprocess_run: MagicMock):
        mock_subprocess_run.side_effect = [""]
        do_selftest()

    @patch("greenbone.feed.sync.main.subprocess.run")
    def test_do_selftest_rsync_fail(self, mock_subprocess_run: MagicMock):
        mock_subprocess_run.side_effect = [PermissionError]
        with self.assertRaisesRegex(
            GreenboneFeedSyncError, "The rsync binary could not be found."
        ):
            do_selftest()


class FeedSyncTestCase(unittest.IsolatedAsyncioTestCase):
    @patch("greenbone.feed.sync.main.do_selftest", autospec=True)
    @patch("greenbone.feed.sync.main.is_root", return_value=False)
    @patch("greenbone.feed.sync.main.Rsync", autospec=True)
    async def test_rsync_timeout_forwarded(
        self,
        rsync_mock: MagicMock,
        is_root_mock: MagicMock,
        selftest_mock: MagicMock,
    ):
        for timeout in (120, 0):
            with self.subTest(timeout=timeout):
                rsync_mock.reset_mock()
                with (
                    temp_directory() as temp_dir,
                    patch.object(
                        sys,
                        "argv",
                        [
                            "greenbone-feed-sync",
                            "--type",
                            "nvt",
                            "--destination-prefix",
                            str(temp_dir),
                            "--rsync-timeout",
                            str(timeout),
                        ],
                    ),
                ):
                    ret = await feed_sync(MagicMock(), MagicMock())

                self.assertEqual(ret, 0)
                rsync_mock.assert_called_once()
                self.assertEqual(
                    rsync_mock.call_args.kwargs.get("timeout"), timeout
                )

    @patch("greenbone.feed.sync.main.do_selftest", autospec=True)
    @patch("greenbone.feed.sync.main.Rsync", autospec=True)
    @patch("greenbone.feed.sync.main.change_user_and_group", autospec=True)
    @patch("greenbone.feed.sync.main.is_root", return_value=True)
    async def test_quiet_still_changes_user_and_group(
        self,
        is_root_mock: MagicMock,
        change_user_mock: MagicMock,
        rsync_mock: MagicMock,
        selftest_mock: MagicMock,
    ):
        console = MagicMock()
        with (
            temp_directory() as temp_dir,
            patch.object(
                sys,
                "argv",
                [
                    "greenbone-feed-sync",
                    "--type",
                    "nvt",
                    "--quiet",
                    "--user",
                    "test-user",
                    "--group",
                    "test-group",
                    "--destination-prefix",
                    str(temp_dir),
                ],
            ),
        ):
            ret = await feed_sync(console, MagicMock())

        self.assertEqual(ret, 0)
        change_user_mock.assert_called_once_with("test-user", "test-group")
        console.print.assert_not_called()

    @patch("greenbone.feed.sync.main.flock_wait", autospec=True)
    @patch("greenbone.feed.sync.main.change_user_and_group", autospec=True)
    @patch("greenbone.feed.sync.main.is_root", return_value=True)
    @patch("greenbone.feed.sync.main.Rsync", autospec=True)
    @patch("greenbone.feed.sync.main.do_selftest", autospec=True)
    async def test_selftest_exits_before_sync(
        self,
        selftest_mock: MagicMock,
        rsync_mock: MagicMock,
        is_root_mock: MagicMock,
        change_user_mock: MagicMock,
        flock_mock: MagicMock,
    ):
        with patch.object(sys, "argv", ["greenbone-feed-sync", "--selftest"]):
            ret = await feed_sync(MagicMock(), MagicMock())

        self.assertEqual(ret, 0)
        selftest_mock.assert_called_once_with()
        change_user_mock.assert_not_called()
        flock_mock.assert_not_called()
        rsync_mock.assert_not_called()

    @patch("greenbone.feed.sync.main.do_selftest", autospec=True)
    @patch("greenbone.feed.sync.main.is_root", return_value=False)
    @patch("greenbone.feed.sync.main.Rsync", autospec=True)
    async def test_continues_after_rsync_error(
        self,
        rsync_mock: MagicMock,
        is_root_mock: MagicMock,
        selftest_mock: MagicMock,
    ):
        rsync_mock.return_value.sync.side_effect = [
            RsyncError(2, [], b"First download failed"),
            None,
        ]
        error_console = MagicMock()
        with (
            temp_directory() as temp_dir,
            patch.object(
                sys,
                "argv",
                [
                    "greenbone-feed-sync",
                    "--type",
                    "nvt",
                    "--destination-prefix",
                    str(temp_dir),
                ],
            ),
        ):
            ret = await feed_sync(MagicMock(), error_console)

        self.assertEqual(ret, 1)
        self.assertEqual(
            [
                awaited.kwargs["destination"]
                for awaited in rsync_mock.return_value.sync.await_args_list
            ],
            [temp_dir / "notus", temp_dir / "openvas/plugins"],
        )
        error_console.print.assert_called_once_with("First download failed")

    @patch("greenbone.feed.sync.main.Rsync", autospec=True)
    @patch("greenbone.feed.sync.main.change_user_and_group", autospec=True)
    @patch("greenbone.feed.sync.main.is_root", autospec=True)
    async def test_do_not_run_as_root(
        self,
        is_root_mock: MagicMock,
        change_user_mock: MagicMock,
        rsync_mock: MagicMock,
    ):
        is_root_mock.return_value = True
        console = MagicMock()
        rsync_mock_instance = rsync_mock.return_value

        with (
            temp_directory() as temp_dir,
            patch.dict(
                "os.environ",
                {"GREENBONE_FEED_SYNC_DESTINATION_PREFIX": str(temp_dir)},
            ),
            patch.object(
                sys,
                "argv",
                [
                    "greenbone-feed-sync",
                    "--type",
                    "nvt",
                ],
            ),
        ):
            ret = await feed_sync(console=console, error_console=console)
            self.assertEqual(ret, 0)

        change_user_mock.assert_called_once_with("gvm", "gvm")
        rsync_mock.assert_called_once_with(
            private_subdir=None,
            verbose=False,
            compression_level=9,
            timeout=None,
            ssh_key=Path("/etc/gvm/greenbone-enterprise-feed-key"),
            change_permissions=True,
        )
        console.print.assert_has_calls(
            [
                call(
                    "Trying to acquire lock on "
                    f"{temp_dir}/openvas/feed-update.lock"
                ),
                call(f"Acquired lock on {temp_dir}/openvas/feed-update.lock"),
                call(f"Releasing lock on {temp_dir}/openvas/feed-update.lock"),
                call(),
            ]
        )

        rsync_mock_instance.sync.assert_has_awaits(
            [
                call(
                    url="rsync://feed.community.greenbone.net/community/"
                    f"vulnerability-feed/{DEFAULT_FEED_RELEASE}/vt-data/notus/",
                    destination=temp_dir / "notus",
                ),
                call(
                    url="rsync://feed.community.greenbone.net/community/"
                    f"vulnerability-feed/{DEFAULT_FEED_RELEASE}/vt-data/nasl/",
                    destination=temp_dir / "openvas/plugins",
                ),
            ]
        )

    @patch("greenbone.feed.sync.main.Rsync", autospec=True)
    async def test_sync_agents_with_enterprise_feed(
        self, rsync_mock: MagicMock
    ):
        console = MagicMock()
        rsync_mock_instance = rsync_mock.return_value

        with (
            temp_directory() as temp_dir,
            patch.dict(
                "os.environ",
                {
                    "GREENBONE_FEED_SYNC_DESTINATION_PREFIX": str(temp_dir),
                    "GREENBONE_FEED_SYNC_ENTERPRISE_FEED_KEY": str(
                        temp_dir / "enterprise.key"
                    ),
                },
            ),
            patch.object(
                sys,
                "argv",
                ["greenbone-feed-sync", "--type", "agent"],
            ),
        ):
            (temp_dir / "enterprise.key").write_text(
                "user@feed.example\n", encoding="utf-8"
            )
            ret = await feed_sync(console=console, error_console=console)

        self.assertEqual(ret, 0)
        rsync_mock_instance.sync.assert_has_awaits(
            [
                call(
                    url=(
                        "ssh://user@feed.example/enterprise/vulnerability-feed/"
                        f"{DEFAULT_FEED_RELEASE}/agent-app/"
                    ),
                    destination=temp_dir / "agent" / "agent-app",
                ),
                call(
                    url=(
                        "ssh://user@feed.example/enterprise/vulnerability-feed/"
                        f"{DEFAULT_FEED_RELEASE}/agent-updater/"
                    ),
                    destination=temp_dir / "agent" / "agent-updater",
                ),
                call(
                    url=(
                        "ssh://user@feed.example/enterprise/vulnerability-feed/"
                        f"{DEFAULT_FEED_RELEASE}/agent-installer/"
                    ),
                    destination=temp_dir / "agent" / "agent-installer",
                ),
            ]
        )

    @patch("greenbone.feed.sync.main.Rsync", autospec=True)
    async def test_sync_all_enterprise(self, rsync_mock: MagicMock):
        console = MagicMock()

        with (
            temp_directory() as temp_dir,
            patch.dict(
                "os.environ",
                {
                    "GREENBONE_FEED_SYNC_DESTINATION_PREFIX": str(temp_dir),
                    "GREENBONE_FEED_SYNC_ENTERPRISE_FEED_KEY": str(
                        temp_dir / "enterprise.key"
                    ),
                },
            ),
            patch.object(
                sys,
                "argv",
                ["greenbone-feed-sync", "--type", "all-enterprise"],
            ),
        ):
            (temp_dir / "enterprise.key").write_text(
                "user@feed.example\n", encoding="utf-8"
            )
            ret = await feed_sync(console=console, error_console=console)

        self.assertEqual(ret, 0)
        feed_url = "ssh://user@feed.example/enterprise"
        vulnerability_url = (
            f"{feed_url}/vulnerability-feed/{DEFAULT_FEED_RELEASE}"
        )
        self.assertEqual(
            rsync_mock.return_value.sync.await_args_list,
            [
                call(
                    url=f"{vulnerability_url}/vt-data/notus/",
                    destination=temp_dir / "notus",
                ),
                call(
                    url=f"{vulnerability_url}/vt-data/nasl/",
                    destination=temp_dir / "openvas/plugins",
                ),
                call(
                    url=f"{vulnerability_url}/agent-app/",
                    destination=temp_dir / "agent/agent-app",
                ),
                call(
                    url=f"{vulnerability_url}/agent-updater/",
                    destination=temp_dir / "agent/agent-updater",
                ),
                call(
                    url=f"{vulnerability_url}/agent-installer/",
                    destination=temp_dir / "agent/agent-installer",
                ),
                call(
                    url=f"{vulnerability_url}/scap-data/",
                    destination=temp_dir / "gvm/scap-data",
                ),
                call(
                    url=f"{vulnerability_url}/cert-data/",
                    destination=temp_dir / "gvm/cert-data",
                ),
                call(
                    url=f"{feed_url}/data-feed/{DEFAULT_FEED_RELEASE}/",
                    destination=temp_dir / "gvm/data-objects/gvmd",
                ),
            ],
        )

    @patch("greenbone.feed.sync.main.Rsync", autospec=True)
    async def test_sync_agents_without_enterprise_feed_key(
        self, rsync_mock: MagicMock
    ):
        console = MagicMock()
        with (
            temp_directory() as temp_dir,
            patch.dict(
                "os.environ",
                {
                    "GREENBONE_FEED_SYNC_DESTINATION_PREFIX": str(temp_dir),
                    "GREENBONE_FEED_SYNC_ENTERPRISE_FEED_KEY": str(
                        temp_dir / "missing-gsf.key"
                    ),
                },
            ),
            patch.object(
                sys,
                "argv",
                ["greenbone-feed-sync", "--type", "agent"],
            ),
        ):
            ret = await feed_sync(console=console, error_console=console)

        self.assertEqual(ret, 0)
        rsync_mock.return_value.sync.assert_has_awaits(
            [
                call(
                    url=(
                        "rsync://feed.community.greenbone.net/community/"
                        f"vulnerability-feed/{DEFAULT_FEED_RELEASE}/agent-app/"
                    ),
                    destination=temp_dir / "agent" / "agent-app",
                ),
                call(
                    url=(
                        "rsync://feed.community.greenbone.net/community/"
                        f"vulnerability-feed/{DEFAULT_FEED_RELEASE}/agent-updater/"
                    ),
                    destination=temp_dir / "agent" / "agent-updater",
                ),
                call(
                    url=(
                        "rsync://feed.community.greenbone.net/community/"
                        f"vulnerability-feed/{DEFAULT_FEED_RELEASE}/agent-installer/"
                    ),
                    destination=temp_dir / "agent" / "agent-installer",
                ),
            ]
        )

    @patch("greenbone.feed.sync.main.Rsync", autospec=True)
    async def test_no_permission_change(self, rsync_mock: MagicMock):
        console = MagicMock()

        with (
            temp_directory() as temp_dir,
            patch.dict(
                "os.environ",
                {"GREENBONE_FEED_SYNC_DESTINATION_PREFIX": str(temp_dir)},
            ),
            patch.object(
                sys,
                "argv",
                [
                    "greenbone-feed-sync",
                    "--type",
                    "nvt",
                    "--no-permission-change",
                ],
            ),
        ):
            ret = await feed_sync(console=console, error_console=console)
            self.assertEqual(ret, 0)

            rsync_mock.assert_called_once_with(
                private_subdir=None,
                verbose=False,
                compression_level=9,
                timeout=None,
                ssh_key=Path("/etc/gvm/greenbone-enterprise-feed-key"),
                change_permissions=False,
            )

    @patch("greenbone.feed.sync.main.Rsync", autospec=True)
    async def test_sync_nvts(self, rsync_mock: MagicMock):
        console = MagicMock()
        rsync_mock_instance = rsync_mock.return_value

        with (
            temp_directory() as temp_dir,
            patch.dict(
                "os.environ",
                {"GREENBONE_FEED_SYNC_DESTINATION_PREFIX": str(temp_dir)},
            ),
            patch.object(
                sys,
                "argv",
                [
                    "greenbone-feed-sync",
                    "--type",
                    "nvt",
                ],
            ),
        ):
            ret = await feed_sync(console=console, error_console=console)
            self.assertEqual(ret, 0)

            rsync_mock.assert_called_once_with(
                private_subdir=None,
                verbose=False,
                compression_level=9,
                timeout=None,
                ssh_key=Path("/etc/gvm/greenbone-enterprise-feed-key"),
                change_permissions=True,
            )
            console.print.assert_has_calls(
                [
                    call(
                        "Trying to acquire lock on "
                        f"{temp_dir}/openvas/feed-update.lock"
                    ),
                    call(
                        f"Acquired lock on {temp_dir}/openvas/feed-update.lock"
                    ),
                    call(
                        f"Releasing lock on {temp_dir}/openvas/feed-update.lock"
                    ),
                    call(),
                ]
            )

            rsync_mock_instance.sync.assert_has_awaits(
                [
                    call(
                        url="rsync://feed.community.greenbone.net/community/"
                        f"vulnerability-feed/{DEFAULT_FEED_RELEASE}/vt-data/notus/",
                        destination=temp_dir / "notus",
                    ),
                    call(
                        url="rsync://feed.community.greenbone.net/community/"
                        f"vulnerability-feed/{DEFAULT_FEED_RELEASE}/vt-data/nasl/",
                        destination=temp_dir / "openvas/plugins",
                    ),
                ]
            )

    @patch("greenbone.feed.sync.main.Rsync", autospec=True)
    async def test_sync_nvts_verbose(self, rsync_mock: MagicMock):
        console = MagicMock()
        rsync_mock_instance = rsync_mock.return_value

        with (
            temp_directory() as temp_dir,
            patch.dict(
                "os.environ",
                {"GREENBONE_FEED_SYNC_DESTINATION_PREFIX": str(temp_dir)},
            ),
            patch.object(
                sys,
                "argv",
                ["greenbone-feed-sync", "--type", "nvt", "-vvv"],
            ),
        ):
            ret = await feed_sync(console=console, error_console=console)
            self.assertEqual(ret, 0)

            rsync_mock.assert_called_once_with(
                private_subdir=None,
                verbose=True,
                compression_level=9,
                timeout=None,
                ssh_key=Path("/etc/gvm/greenbone-enterprise-feed-key"),
                change_permissions=True,
            )
            console.print.assert_has_calls(
                [
                    call(
                        "Trying to acquire lock on "
                        f"{temp_dir}/openvas/feed-update.lock"
                    ),
                    call(
                        f"Acquired lock on {temp_dir}/openvas/feed-update.lock"
                    ),
                    call(
                        "Downloading Notus files from "
                        "rsync://feed.community.greenbone.net/community/"
                        f"vulnerability-feed/{DEFAULT_FEED_RELEASE}/vt-data/notus/ "
                        f"to {temp_dir}/notus"
                    ),
                    call(),
                    call(
                        "Downloading NASL files from "
                        "rsync://feed.community.greenbone.net/community/"
                        f"vulnerability-feed/{DEFAULT_FEED_RELEASE}/vt-data/nasl/ "
                        f"to {temp_dir}/openvas/plugins"
                    ),
                    call(),
                    call(
                        f"Releasing lock on {temp_dir}/openvas/feed-update.lock"
                    ),
                    call(),
                ]
            )

            rsync_mock_instance.sync.assert_has_awaits(
                [
                    call(
                        url="rsync://feed.community.greenbone.net/community/"
                        f"vulnerability-feed/{DEFAULT_FEED_RELEASE}/vt-data/notus/",
                        destination=temp_dir / "notus",
                    ),
                    call(
                        url="rsync://feed.community.greenbone.net/community/"
                        f"vulnerability-feed/{DEFAULT_FEED_RELEASE}/vt-data/nasl/",
                        destination=temp_dir / "openvas/plugins",
                    ),
                ]
            )

    @patch("greenbone.feed.sync.main.Rsync", autospec=True)
    async def test_sync_nvts_quiet(self, rsync_mock: MagicMock):
        console = MagicMock()
        rsync_mock_instance = rsync_mock.return_value

        with (
            temp_directory() as temp_dir,
            patch.dict(
                "os.environ",
                {"GREENBONE_FEED_SYNC_DESTINATION_PREFIX": str(temp_dir)},
            ),
            patch.object(
                sys,
                "argv",
                ["greenbone-feed-sync", "--type", "nvt", "--quiet"],
            ),
        ):
            ret = await feed_sync(console=console, error_console=console)
            self.assertEqual(ret, 0)

            rsync_mock.assert_called_once_with(
                private_subdir=None,
                verbose=False,
                compression_level=9,
                timeout=None,
                ssh_key=Path("/etc/gvm/greenbone-enterprise-feed-key"),
                change_permissions=True,
            )
            console.print.assert_not_called()

            rsync_mock_instance.sync.assert_has_awaits(
                [
                    call(
                        url="rsync://feed.community.greenbone.net/community/"
                        f"vulnerability-feed/{DEFAULT_FEED_RELEASE}/vt-data/notus/",
                        destination=temp_dir / "notus",
                    ),
                    call(
                        url="rsync://feed.community.greenbone.net/community/"
                        f"vulnerability-feed/{DEFAULT_FEED_RELEASE}/vt-data/nasl/",
                        destination=temp_dir / "openvas/plugins",
                    ),
                ]
            )

    @patch("greenbone.feed.sync.main.Rsync", autospec=True)
    async def test_sync_nvts_rsync_error(self, rsync_mock: MagicMock):
        console = MagicMock()
        rsync_mock_instance = rsync_mock.return_value
        rsync_mock_instance.sync.side_effect = RsyncError(
            2, [], b"An rsync error"
        )

        with (
            temp_directory() as temp_dir,
            patch.dict(
                "os.environ",
                {"GREENBONE_FEED_SYNC_DESTINATION_PREFIX": str(temp_dir)},
            ),
            patch.object(
                sys,
                "argv",
                ["greenbone-feed-sync", "--type", "nvt", "--fail-fast"],
            ),
        ):
            ret = await feed_sync(console=console, error_console=console)
            self.assertEqual(ret, 1)
            rsync_mock_instance.sync.assert_awaited_once()

            rsync_mock.assert_called_once_with(
                private_subdir=None,
                verbose=False,
                compression_level=9,
                timeout=None,
                ssh_key=Path("/etc/gvm/greenbone-enterprise-feed-key"),
                change_permissions=True,
            )
            console.print.assert_has_calls(
                [
                    call(
                        "Trying to acquire lock on "
                        f"{temp_dir}/openvas/feed-update.lock"
                    ),
                    call(
                        f"Acquired lock on {temp_dir}/openvas/feed-update.lock"
                    ),
                    call("An rsync error"),
                    call(
                        f"Releasing lock on {temp_dir}/openvas/feed-update.lock"
                    ),
                ]
            )

            rsync_mock_instance.sync.assert_has_awaits(
                [
                    call(
                        url="rsync://feed.community.greenbone.net/community/"
                        f"vulnerability-feed/{DEFAULT_FEED_RELEASE}/vt-data/notus/",
                        destination=temp_dir / "notus",
                    ),
                ]
            )


class MainFunctionTestCase(unittest.TestCase):
    @patch("greenbone.feed.sync.main.Console", autospec=True)
    @patch("greenbone.feed.sync.main.feed_sync", autospec=True)
    def test_keyboard_interrupt(
        self, feed_sync_mock: MagicMock, console_mock: MagicMock
    ):
        feed_sync_mock.side_effect = KeyboardInterrupt

        with self.assertRaises(SystemExit) as cm:
            main()

        self.assertEqual(cm.exception.code, 1)
        feed_sync_mock.assert_awaited_once()

    @patch("greenbone.feed.sync.main.Console")
    @patch("greenbone.feed.sync.main.Rsync", autospec=True)
    def test_sync_nvts(self, rsync_mock: MagicMock, console_mock: MagicMock):
        rsync_mock_instance = rsync_mock.return_value
        console_mock_instance = console_mock.return_value

        with (
            temp_directory() as temp_dir,
            patch.dict(
                "os.environ",
                {"GREENBONE_FEED_SYNC_DESTINATION_PREFIX": str(temp_dir)},
            ),
            patch.object(
                sys,
                "argv",
                [
                    "greenbone-feed-sync",
                    "--type",
                    "nvt",
                ],
            ),
        ):
            with self.assertRaises(SystemExit) as cm:
                main()

            self.assertEqual(cm.exception.code, 0)

            rsync_mock.assert_called_once_with(
                private_subdir=None,
                verbose=False,
                compression_level=9,
                timeout=None,
                ssh_key=Path("/etc/gvm/greenbone-enterprise-feed-key"),
                change_permissions=True,
            )
            console_mock_instance.print.assert_has_calls(
                [
                    call(
                        "Trying to acquire lock on "
                        f"{temp_dir}/openvas/feed-update.lock"
                    ),
                    call(
                        f"Acquired lock on {temp_dir}/openvas/feed-update.lock"
                    ),
                    call(
                        f"Releasing lock on {temp_dir}/openvas/feed-update.lock"
                    ),
                    call(),
                ]
            )

            rsync_mock_instance.sync.assert_has_awaits(
                [
                    call(
                        url="rsync://feed.community.greenbone.net/community/"
                        f"vulnerability-feed/{DEFAULT_FEED_RELEASE}/vt-data/notus/",
                        destination=temp_dir / "notus",
                    ),
                    call(
                        url="rsync://feed.community.greenbone.net/community/"
                        f"vulnerability-feed/{DEFAULT_FEED_RELEASE}/vt-data/nasl/",
                        destination=temp_dir / "openvas/plugins",
                    ),
                ]
            )

    @patch("greenbone.feed.sync.main.Console")
    @patch("greenbone.feed.sync.main.Rsync", autospec=True)
    def test_sync_nvts_error(
        self, rsync_mock: MagicMock, console_mock: MagicMock
    ):
        rsync_mock_instance = rsync_mock.return_value
        console_mock_instance = console_mock.return_value
        rsync_mock_instance.sync.side_effect = GreenboneFeedSyncError(
            "An error"
        )

        with (
            temp_directory() as temp_dir,
            patch.dict(
                "os.environ",
                {"GREENBONE_FEED_SYNC_DESTINATION_PREFIX": str(temp_dir)},
            ),
            patch.object(
                sys,
                "argv",
                ["greenbone-feed-sync", "--type", "nvt", "--fail-fast"],
            ),
        ):
            with self.assertRaises(SystemExit) as cm:
                main()

            self.assertEqual(cm.exception.code, 1)

            rsync_mock.assert_called_once_with(
                private_subdir=None,
                verbose=False,
                compression_level=9,
                timeout=None,
                ssh_key=Path("/etc/gvm/greenbone-enterprise-feed-key"),
                change_permissions=True,
            )
            console_mock_instance.print.assert_has_calls(
                [
                    call(
                        "Trying to acquire lock on "
                        f"{temp_dir}/openvas/feed-update.lock"
                    ),
                    call(
                        f"Acquired lock on {temp_dir}/openvas/feed-update.lock"
                    ),
                    call(
                        f"Releasing lock on {temp_dir}/openvas/feed-update.lock"
                    ),
                    call("[red]❌[/red]Error: An error"),
                ]
            )

            rsync_mock_instance.sync.assert_has_awaits(
                [
                    call(
                        url="rsync://feed.community.greenbone.net/community/"
                        f"vulnerability-feed/{DEFAULT_FEED_RELEASE}/vt-data/notus/",
                        destination=temp_dir / "notus",
                    ),
                ]
            )
