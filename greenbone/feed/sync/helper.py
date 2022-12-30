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
import errno
import fcntl
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Iterable, Union

from greenbone.feed.sync.errors import (
    ExecProcessError,
    FileLockingError,
    GreenboneFeedSyncError,
)


async def exec_command(
    *cmd: Iterable[str], capture_output: bool = False
) -> None:
    """
    Run a command as subprocess

    Argument:
        cmd: Command with arguments to run as subprocess
    """
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stderr=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE if capture_output else None,
    )
    stdout, stderr = await process.communicate()
    returncode = await process.wait()
    if returncode:
        raise ExecProcessError(returncode, cmd, stdout=stdout, stderr=stderr)


def ospd_openvas_version() -> str:
    """
    Get the version string from ospd-openvas
    """
    try:
        # pylint: disable=import-outside-toplevel
        from ospd_openvas import __version__ as version

        return version
    except ImportError:
        raise GreenboneFeedSyncError(
            "Could not determine version of ospd-openvas. "
            "Unable to load ospd_openvas Python module. "
            "Please ensure that ospd-openvas is installed or set a feed "
            "version explicitly."
        ) from None


def ospd_openvas_feed_version() -> str:
    """
    Derive the feed version from the ospd-openvas version
    """
    version = ospd_openvas_version()
    versions = version.split(".", 2)

    major, minor = versions[0:2]
    if len(minor) == 1:
        minor = f"0{minor}"
    return f"{major}.{minor}"


@contextmanager
def flock(path: Union[str, Path]) -> Generator[None, None, None]:
    """
    Lock a file

    Arguments:
        path: File to lock
    """
    # ensure path is a Path
    path = Path(path)

    # ensure parent directories exist
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        raise FileLockingError(
            f"Could not create parent directories for {path}"
        ) from None

    fd0 = path.open("w", encoding="utf8")

    try:
        fcntl.flock(fd0, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as e:
        if e.errno in (errno.EAGAIN, errno.EACCES):
            raise FileLockingError(
                f"{path} is locked. Another process related to the feed update "
                "may already running."
            ) from None
        raise
    try:
        yield
    finally:
        try:
            # free the lock
            fcntl.flock(fd0, fcntl.LOCK_UN)
            fd0.close()
        except OSError:
            pass
