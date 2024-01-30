# SPDX-FileCopyrightText: 2024 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

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


from typing import Iterable, Optional


class GreenboneFeedSyncError(Exception):
    """
    Base exception class
    """


class ConfigFileError(GreenboneFeedSyncError):
    """
    Error while processing a config file
    """


class ExecProcessError(GreenboneFeedSyncError):
    """
    Error while executing a process
    """

    def __init__(
        self,
        returncode: int,
        cmd: Iterable[str],
        *,
        stdout: Optional[bytes] = None,
        stderr: Optional[bytes] = None,
    ) -> None:
        self.returncode = returncode
        self.cmd = cmd
        self.stout = (
            None if not stdout else stdout.decode("utf8", errors="ignore")
        )
        self.stderr = (
            None if not stderr else stderr.decode("utf8", errors="ignore")
        )

    def __str__(self):
        cmd = " ".join(self.cmd)
        return f"'{cmd}' returned non-zero exit status {self.returncode}."


class RsyncError(ExecProcessError):
    """
    Error while running rsync
    """

    def __init__(
        self,
        returncode: int,
        args: Iterable[str],
        stderr: Optional[bytes] = None,
    ) -> None:
        super().__init__(returncode, cmd=["rsync"] + list(args), stderr=stderr)


class FileLockingError(GreenboneFeedSyncError):
    """
    An error during locking a file
    """
