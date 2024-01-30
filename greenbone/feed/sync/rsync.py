# SPDX-FileCopyrightText: 2022-2024 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import asyncio
import os
from pathlib import Path
from typing import Iterable, Optional, Union
from urllib.parse import urlsplit

from greenbone.feed.sync.errors import RsyncError


async def exec_rsync(*args: str) -> None:
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
DEFAULT_RSYNC_TIMEOUT: Optional[int] = (
    None  # in seconds. 0 means no timeout and None use rsync default
)
DEFAULT_RSYNC_SSH_PORT = 24
DEFAULT_RSYNC_SSH_OPTS = (
    "-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
)

PathLike = Union[os.PathLike, str]


class Rsync:
    """
    Class to sync the feed data via rsync

    Args:
        verbose: Enable verbose output
        private_subdir: A private directory to exclude from from the sync
        compression_level: Set an compression level explicitly.
            Default is 9 (highest).
        timeout: Set a specific timeout in seconds. Default timeout of rsync is
            used of not set explicitly. 0 for no timeout.
        ssh_key: SSH key for using ssh as rsync transport protocol.
        exclude: An iterable of directories to exclude from the sync.

    """

    def __init__(
        self,
        *,
        verbose: bool = False,
        private_subdir: Optional[PathLike] = None,
        compression_level: Optional[int] = DEFAULT_RSYNC_COMPRESSION_LEVEL,
        timeout: Optional[int] = DEFAULT_RSYNC_TIMEOUT,
        ssh_key: Optional[PathLike] = None,
        exclude: Optional[Iterable[PathLike]] = None,
    ) -> None:
        self.verbose = verbose
        self.private_subdir = private_subdir
        self.compression_level = compression_level
        self.timeout = timeout
        self.ssh_key = ssh_key
        self.exclude = exclude

    async def sync(self, url: str, destination: PathLike) -> None:
        """
        Sync data from a remote URL to a destination path

        Args:
            url: URL to sync
            destination: Path to store the downloaded data
        """
        dest = Path(destination)
        dest.mkdir(parents=True, exist_ok=True)
        splitted_url = urlsplit(url)

        rsync_default_options = [
            "--links",
            "--times",
            "--omit-dir-times",
            "--recursive",
            "--partial",
            "--progress",
        ]

        if "ssh" in splitted_url.scheme:
            port = splitted_url.port or DEFAULT_RSYNC_SSH_PORT
            # we use ssh now
            rsync_ssh_options = [
                "-e",
                f"ssh {DEFAULT_RSYNC_SSH_OPTS} -p {port} -i '{self.ssh_key}'",
            ]
            url = f"{splitted_url.netloc}:{splitted_url.path}"
        else:
            rsync_ssh_options = []

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
            rsync_delete.extend(["--exclude", os.fspath(self.private_subdir)])

        if self.exclude:
            for exclude in self.exclude:
                rsync_delete.extend(["--exclude", os.fspath(exclude)])

        rsync_verbose = ["-v"] if self.verbose else ["-q"]

        args = (
            rsync_default_options
            + rsync_ssh_options
            + rsync_timeout
            + rsync_verbose
            + rsync_compress
            + rsync_delete
            + rsync_chmod
            + rsync_links
            + [url, str(dest.absolute())]
        )

        await exec_rsync(*args)
