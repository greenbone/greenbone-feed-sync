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
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator, Iterable, Optional, Union

from greenbone.feed.sync.errors import ExecProcessError, FileLockingError

DEFAULT_FLOCK_WAIT_INTERVAL = 5  # in seconds


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


@asynccontextmanager
async def flock_wait(
    path: Union[str, Path],
    *,
    wait_interval: Optional[int] = DEFAULT_FLOCK_WAIT_INTERVAL,
    verbose: bool = False,
) -> AsyncGenerator[None, None]:
    """
    Try to lock a file and wait if it is already locked

    Arguments:
        path: File to lock
        wait_interval: Time to wait in seconds after failed lock attempt before
            re-trying to lock the file. Set to None to raise a FileLockingError
            instead of re-trying to acquire the lock. Default is 5 seconds.
        verbose: Set to True to print locking messages to stdout. Default is
            False.
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

    has_lock = False
    while not has_lock:
        try:
            if verbose:
                print(f"Trying to acquire lock on {path.absolute()}")

            fcntl.flock(fd0, fcntl.LOCK_EX | fcntl.LOCK_NB)

            if verbose:
                print(f"Acquired lock on {path.absolute()}")

            has_lock = True
        except OSError as e:
            if e.errno in (errno.EAGAIN, errno.EACCES):
                if wait_interval is None:
                    raise FileLockingError(
                        f"{path.absolute()} is locked. Another process related "
                        "to the feed update may already running."
                    ) from None

                if verbose:
                    print(
                        f"{path.absolute()} is locked by another process. "
                        f"Waiting {wait_interval} seconds before next try."
                    )
                await asyncio.sleep(wait_interval)
            else:
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
