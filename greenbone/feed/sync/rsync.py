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
from pathlib import Path
from typing import Iterable, Optional, Union

from greenbone.feed.sync.errors import RsyncError


async def exec_rsync(*args: Iterable[str]) -> None:
    """
    Run rsync

    Argument:
        args: Arguments for rsync
    """
    process = await asyncio.create_subprocess_exec(
        "rsync", *args, stderr=asyncio.subprocess.PIPE
    )
    _, stderr = await process.communicate()
    returncode = await process.wait()
    if returncode:
        raise RsyncError(returncode, args, stderr=stderr)


DEFAULT_RSYNC_URL = "rsync://feed.community.greenbone.net/community"
DEFAULT_RSYNC_COMPRESSION_LEVEL = 9
DEFAULT_RSYNC_TIMEOUT = (
    None  # in seconds. 0 means no timeout and None use rsync default
)


class Rsync:
    """
    Class to sync the feed data via rsync
    """

    def __init__(
        self,
        *,
        verbose: bool = False,
        private_subdir: Optional[Path] = None,
        compression_level: Optional[int] = DEFAULT_RSYNC_COMPRESSION_LEVEL,
        timeout: Optional[int] = DEFAULT_RSYNC_TIMEOUT,
    ) -> None:
        self.verbose = verbose
        self.private_subdir = private_subdir
        self.compression_level = compression_level
        self.timeout = timeout

    async def sync(self, url: str, destination: Union[str, Path]) -> None:
        """
        Sync data from a remote URL to a destination path

        Args:
            url: URL to sync
            destination: Path to store the downloaded data
        """
        destination: Path = Path(destination)
        destination.mkdir(parents=True, exist_ok=True)

        rsync_default_options = [
            "--links",
            "--times",
            "--omit-dir-times",
            "--recursive",
            "--partial",
            "--progress",
        ]

        rsync_timeout = (
            [
                f"--timeout={self.timeout}",
            ]
            if self.timeout is not None
            else []
        )

        rsync_compress = (
            [
                f"--compress-level={self.compression_level}",
            ]
            if self.compression_level is not None
            else []
        )

        rsync_delete = [
            "--delete",
        ]

        rsync_chmod = [
            "--perms",
            "--chmod=Fugo+r,Fug+w,Dugo-s,Dugo+rx,Dug+w",
        ]

        rsync_links = [
            "--copy-unsafe-links",
            "--hard-links",
        ]

        if self.private_subdir:
            rsync_delete.extend(["--exclude", self.private_subdir])

        rsync_verbose = ["-v"] if self.verbose else ["-q"]

        args = (
            rsync_default_options
            + rsync_timeout
            + rsync_verbose
            + rsync_compress
            + rsync_delete
            + rsync_chmod
            + rsync_links
            + [url, str(destination.absolute())]
        )

        await exec_rsync(*args)
