# Copyright (C) 2022 Greenbone Networks GmbH
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
import os
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import NoReturn, Optional

from greenbone.feed.sync.errors import GreenboneFeedSyncError
from greenbone.feed.sync.helper import flock, ospd_openvas_feed_version
from greenbone.feed.sync.rsync import (
    DEFAULT_NASL_PATH,
    DEFAULT_NOTUS_PATH,
    DEFAULT_RSYNC_COMPRESSION_LEVEL,
    DEFAULT_RSYNC_URL,
    Rsync,
)

__all__ = ("main",)


def to_lower(value: str) -> str:
    """
    Convert a string argparser value to lower case
    """
    return value.lower()


def create_parser() -> ArgumentParser:
    """
    Create an ArgumentParser for the feed sync CLI
    """
    parser = ArgumentParser()
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--private-directory",
        help="(Sub-)Directory to exclude from the sync which will never get "
        "deleted automatically.",
        type=Path,
    )
    parser.add_argument(
        "--feed-version",
        choices=[
            "21.04",
            "22.04",
        ],
        help="Feed version to sync. If not provided ospd-openvas must be "
        "installed and the feed version will be derived from the installed "
        "ospd-openvas version.",
    )
    parser.add_argument(
        "--compression-level",
        type=int,
        choices=range(0, 10),
        default=DEFAULT_RSYNC_COMPRESSION_LEVEL,
        help="Compression level (0-9). Default: %(default)s",
    )
    parser.add_argument(
        "--type",
        choices=["notus", "nasl", "all"],
        default="all",
        type=to_lower,
        help="Default: %(default)s",
    )
    parser.add_argument(
        "--rsync-url",
        default=DEFAULT_RSYNC_URL,
        help="Default: %(default)s",
    )
    parser.add_argument(
        "--notus-destination",
        type=Path,
        default=DEFAULT_NOTUS_PATH,
        help="Default: %(default)s",
    )
    parser.add_argument(
        "--notus-url",
        help="Default: $RSYNC_URL:/community/vulnerability-feed/$FEED_VERSION/"
        "vt-data/notus",
    )
    parser.add_argument(
        "--nasl-destination",
        type=Path,
        default=DEFAULT_NASL_PATH,
        help="Default: %(default)s",
    )
    parser.add_argument(
        "--nasl-url",
        help="Default: $RSYNC_URL:/community/vulnerability-feed/$FEED_VERSION/"
        "vt-data/nasl",
    )
    parser.add_argument(
        "--lock-file",
        "--lockfile",
        type=Path,
        default="/var/lib/openvas/feed-update.lock",
        help="Default: %(default)s",
    )
    return parser


def is_root() -> bool:
    """
    Checks if the current user is root
    """
    return os.geteuid() == 0


def create_rsync_task(
    rsync: Rsync,
    rsync_url: str,
    data_path: Path,
    destination: str,
    full_url: Optional[str] = None,
) -> asyncio.Task:
    if full_url:
        url = full_url
    else:
        url = f"{rsync_url}:{data_path}"

    return asyncio.create_task(rsync.sync(url=url, destination=destination))


async def feed_sync() -> None:
    """
    Sync the feeds
    """
    if is_root():
        raise GreenboneFeedSyncError(
            "The sync script should not be run as root. Running the script as "
            "root may cause several hard to find permissions issues."
        )

    parser = create_parser()
    args = parser.parse_args()

    feed_version = args.feed_version
    if not feed_version:
        feed_version = ospd_openvas_feed_version()

    rsync = Rsync(
        private_subdir=args.private_directory,
        verbose=args.verbose,
        compression_level=args.compression_level,
    )

    data_base_path = f"/community/vulnerability-feed/{feed_version}"

    with flock(args.lock_file):
        tasks = []
        if args.type in ("notus", "all"):
            notus_data_path = f"{data_base_path}/vt-data/notus/"
            tasks.append(
                create_rsync_task(
                    rsync,
                    args.rsync_url,
                    notus_data_path,
                    args.notus_destination,
                    args.notus_url,
                )
            )
        if args.type in ("nasl", "all"):
            nasl_data_path = f"{data_base_path}/vt-data/nasl/"
            tasks.append(
                create_rsync_task(
                    rsync,
                    args.rsync_url,
                    nasl_data_path,
                    args.nasl_destination,
                    args.nasl_url,
                )
            )

        for task in asyncio.as_completed(tasks):
            await task


def main() -> NoReturn:
    """
    Main CLI function
    """
    try:
        asyncio.run(feed_sync())
        sys.exit(0)
    except GreenboneFeedSyncError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == "__main__":
    main()
