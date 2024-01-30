# SPDX-FileCopyrightText: 2022-2024 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import asyncio
import subprocess
import sys
from dataclasses import dataclass
from typing import Iterable, NoReturn

from rich.console import Console

from greenbone.feed.sync.config import DEFAULT_VERBOSITY
from greenbone.feed.sync.errors import GreenboneFeedSyncError, RsyncError
from greenbone.feed.sync.helper import (
    Spinner,
    change_user_and_group,
    flock_wait,
    is_root,
)
from greenbone.feed.sync.parser import CliParser
from greenbone.feed.sync.rsync import Rsync

__all__ = ("main",)


@dataclass
class Sync:
    """
    Class to store sync information
    """

    name: str
    types: Iterable[str]
    url: str
    destination: str


@dataclass
class SyncList:
    """
    Class to store a list of sync information
    """

    lock_file: str
    syncs: Iterable[Sync]


def filter_syncs(lock_file: str, feed_type: str, *syncs: Sync) -> SyncList:
    """
    Create a list of syncs which only match to the feed type
    """
    return SyncList(
        lock_file=lock_file,
        syncs=[sync for sync in syncs if feed_type in sync.types],
    )


def do_selftest() -> None:
    """
    Check for rsync command.
    """
    try:
        subprocess.run(
            ["rsync", "--help"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    except (PermissionError, FileNotFoundError, subprocess.CalledProcessError):
        raise GreenboneFeedSyncError(
            "The rsync binary could not be found."
        ) from None


async def feed_sync(console: Console, error_console: Console) -> int:
    """
    Sync the feeds
    """
    parser = CliParser()
    args = parser.parse_arguments()

    do_selftest()

    if args.selftest:
        return 0

    if args.quiet:
        verbose = 0
    else:
        verbose = DEFAULT_VERBOSITY if args.verbose is None else args.verbose

    if is_root():
        if verbose >= 1:
            console.print(
                f"Running as root. Switching to user '{args.user}' and "
                f"group '{args.group}'."
            )
            change_user_and_group(args.user, args.group)

    rsync = Rsync(
        private_subdir=args.private_directory,
        verbose=verbose >= 3,
        compression_level=args.compression_level,
        ssh_key=args.greenbone_enterprise_feed_key,
    )

    openvas_syncs = filter_syncs(
        args.openvas_lock_file,
        args.type,
        Sync(
            name="Notus files",
            types=("notus", "nvt", "all"),
            url=args.notus_url,
            destination=args.notus_destination,
        ),
        Sync(
            name="NASL files",
            types=("nasl", "nvt", "all"),
            url=args.nasl_url,
            destination=args.nasl_destination,
        ),
    )
    gvmd_syncs = filter_syncs(
        args.gvmd_lock_file,
        args.type,
        Sync(
            name="SCAP data",
            types=("scap", "all"),
            url=args.scap_data_url,
            destination=args.scap_data_destination,
        ),
        Sync(
            name="CERT-Bund data",
            types=("cert", "all"),
            url=args.cert_data_url,
            destination=args.cert_data_destination,
        ),
        Sync(
            name="gvmd data",
            types=("gvmd-data", "all"),
            url=args.gvmd_data_url,
            destination=args.gvmd_data_destination,
        ),
        Sync(
            name="report formats",
            types=("report-format"),
            url=args.report_formats_url,
            destination=args.report_formats_destination,
        ),
        Sync(
            name="scan configs",
            types=("scan-config"),
            url=args.scan_configs_url,
            destination=args.scan_configs_destination,
        ),
        Sync(
            name="port lists",
            types=("port-list"),
            url=args.port_lists_url,
            destination=args.port_lists_destination,
        ),
    )

    has_error = False
    wait_interval = None if args.no_wait else args.wait_interval

    for sync_list in (openvas_syncs, gvmd_syncs):
        if not sync_list.syncs:
            continue

        async with flock_wait(
            sync_list.lock_file,
            console=console if verbose else None,
            wait_interval=wait_interval,
        ):
            for sync in sync_list.syncs:
                try:
                    rsync_coro = rsync.sync(
                        url=sync.url, destination=sync.destination
                    )
                    if verbose >= 3:
                        console.print(
                            f"Downloading {sync.name} from {sync.url} to "
                            f"{sync.destination}"
                        )
                        await rsync_coro
                        # add newline after rsync
                        console.print()
                    elif verbose >= 1:
                        with Spinner(
                            console,
                            f"Downloading {sync.name} from {sync.url} to "
                            f"{sync.destination}",
                        ):
                            await rsync_coro
                    else:
                        await rsync_coro
                except RsyncError as e:
                    has_error = True
                    error_console.print(e.stderr)
                    if args.fail_fast:
                        return 1

        if verbose >= 2:
            # add newline for grouping lock
            console.print()

    return 1 if has_error else 0


def main() -> NoReturn:
    """
    Main CLI function
    """
    console = Console()
    error_console = Console(stderr=True)

    try:
        sys.exit(asyncio.run(feed_sync(console, error_console)))
    except GreenboneFeedSyncError as e:
        error_console.print(f"[red]❌[/red]Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == "__main__":
    main()
