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
import os
import shutil
from contextlib import asynccontextmanager
from pathlib import Path
from types import TracebackType
from typing import AsyncGenerator, Optional, Type, Union

from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner as RichSpinner

from greenbone.feed.sync.errors import FileLockingError

DEFAULT_FLOCK_WAIT_INTERVAL = 5  # in seconds


def is_root() -> bool:
    """
    Checks if the current user is root
    """
    return os.geteuid() == 0


@asynccontextmanager
async def flock_wait(
    path: Union[str, Path],
    *,
    console: Optional[Console] = None,
    wait_interval: Optional[int] = DEFAULT_FLOCK_WAIT_INTERVAL,
) -> AsyncGenerator[None, None]:
    """
    Try to lock a file and wait if it is already locked

    Arguments:
        path: File to lock
        console: A console to print messages to or None to keep the function
            quiet.
        wait_interval: Time to wait in seconds after failed lock attempt before
            re-trying to lock the file. Set to None to raise a FileLockingError
            instead of re-trying to acquire the lock. Default is 5 seconds.
    """
    # ensure path is a Path
    path = Path(path)

    # ensure parent directories exist
    try:
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o770)
    except OSError as e:
        raise FileLockingError(
            f"Could not create parent directories for {path}"
        ) from e

    with path.open("w", encoding="utf8") as fd0:
        has_lock = False
        while not has_lock:
            try:
                if console:
                    console.print(
                        f"Trying to acquire lock on {path.absolute()}"
                    )

                fcntl.flock(fd0, fcntl.LOCK_EX | fcntl.LOCK_NB)

                if console:
                    console.print(f"Acquired lock on {path.absolute()}")

                has_lock = True
                path.chmod(mode=0o660)
            except OSError as e:
                if e.errno in (errno.EAGAIN, errno.EACCES):
                    if wait_interval is None:
                        raise FileLockingError(
                            f"{path.absolute()} is locked. Another process "
                            "related to the feed update may already running."
                        ) from None

                    if console:
                        console.print(
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
                if console:
                    console.print(f"Releasing lock on {path.absolute()}")

                fcntl.flock(fd0, fcntl.LOCK_UN)
            except OSError:
                pass


class Spinner:
    def __init__(self, console: Console, status: str) -> None:
        self._spinner = RichSpinner(
            "dots", text=status, style="status.spinner", speed=1.0
        )
        self._live = Live(
            self._spinner,
            console=console,
            refresh_per_second=12.5,
            transient=False,
        )

    def __enter__(self) -> "Spinner":
        self._live.start()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self._live.stop()


def change_user_and_group(
    user: Union[str, int], group: Union[str, int]
) -> None:
    """
    Change effective user or group of the current running process

    Args:
        user: User name or ID
        group: Group name or ID
    """
    if isinstance(user, str):
        user = shutil._get_uid(user)  # pylint: disable=protected-access
    if isinstance(group, str):
        group = shutil._get_gid(group)  # pylint: disable=protected-access

    os.setegid(group)
    os.seteuid(user)
