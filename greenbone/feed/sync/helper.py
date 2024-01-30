# SPDX-FileCopyrightText: 2022-2024 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

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

from greenbone.feed.sync.errors import FileLockingError, GreenboneFeedSyncError

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
    wait_interval: Optional[Union[int, float]] = DEFAULT_FLOCK_WAIT_INTERVAL,
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
        user_id = shutil._get_uid(  # type: ignore[attr-defined] # pylint: disable=protected-access # noqa: E501
            user
        )
        if user_id is None:
            raise GreenboneFeedSyncError(
                f"Can't run as user '{user}'. User '{user}' is unknown."
            )
        user = user_id
    if isinstance(group, str):
        group_id = shutil._get_gid(group)  # type: ignore[attr-defined] # pylint: disable=protected-access # noqa: E501
        if group_id is None:
            raise GreenboneFeedSyncError(
                f"Can't run as group '{group}'. Group '{group}' is unknown."
            )
        group = group_id

    os.setegid(group)  # type: ignore[arg-type]
    os.seteuid(user)  # type: ignore[arg-type]
