"""
Flood Modeller Python API
Copyright (C) 2025 Jacobs U.K. Limited

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see https://www.gnu.org/licenses/.

If you have any query about this program or this License, please contact us at support@floodmodeller.com or write to the following
address: Jacobs UK Limited, Flood Modeller, Cottons Centre, Cottons Lane, London, SE1 2QG, United Kingdom.
"""

from __future__ import annotations

import filecmp
import logging
import re
import tempfile
from datetime import datetime
from hashlib import sha1
from pathlib import Path
from shutil import copy

import pandas as pd

from .to_from_json import Jsonable


class BackupControl(Jsonable):
    """
    The BackupControl class provides functionality for creating and managing file backups.


    Attributes:
        temp_dir (str): The temporary directory used for backups.
        backup_dirname (str): The name of the backup directory.
        backup_dir (str): The full path to the backup directory.
        backup_csv_path (str): The full path to the backup CSV file.

    Methods:
        _init_backup(): Initialises the backup directory and creates a CSV file for logging backup information.
        clear_backup(): Removes all backup files in the backup directory.

    Usage:
        The BackUp class can be used to create backups of files and directories. The backups are stored in a temporary
        directory and are logged in a CSV file. The backups can be cleared using the clear_backup method.

    Example:
        # Create a new BackUp object
        backup = BackUp(backup_directory_name='my_backups')

        # Create a backup of a file
        backup_file_path = '/path/to/my/file.txt'
        backup.backup_file(backup_file_path)

        # Clear all backups
        backup.clear_backup()
    """

    def __init__(self):
        """
        Initialises a new BackUp object.

        Args:
            backup_directory_name (str): The name of the backup directory. Defaults to "floodmodeller_api_backup".
        """
        self.temp_dir = tempfile.gettempdir()
        self.backup_dirname = "floodmodeller_api_backup"
        self.backup_dir = Path(self.temp_dir, self.backup_dirname)
        self.backup_csv_path = Path(self.backup_dir, "file-backups.csv")
        self._init_backup()

    def _init_backup(self):
        """
        Initialises the backup directory and creates a CSV file for logging backup information.
        """
        # Create the backup directory if it doesn't exist
        if not self.backup_dir.exists():
            self.backup_dir.mkdir()
            logging.info(
                "%s: Initialised backup directory at %s",
                self.__class__.__name__,
                self.backup_dir,
            )

        # Create the backup CSV file if it doesn't exist
        if not self.backup_csv_path.exists():
            with open(self.backup_csv_path, "w") as f:
                f.write("path,file_id,dttm\n")

    def clear_backup(self, file_id="*"):
        """
        Removes all backup files in the backup directory.
        Args:
            file_id (str): The ID of the file to clear, default value is "*" to clear all files
                If this is called from the file class then the file Id of that file will be used
        """
        # If the user wants to clear a specific file, then suffix * to match it
        if file_id != "*":
            file_id = f"{file_id}*"

        files = self.backup_dir.glob(file_id)
        for f in files:
            Path(f).unlink()


def parse_backup_dttm(path):
    # Extract datetime from string
    datetime_str = re.search(r"\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}", path).group(0)
    # Convert datetime string to datetime object
    return datetime.strptime(datetime_str, "%Y-%m-%d-%H-%M-%S")


class BackupFile:
    """
    Defines a backed up file and functionality to restore it

    Args:
        path (str): The path to the file that you want to back up or retrieve.
        file_id (str): A unique identifier for the file generated by hashing its absolute path.

    Attributes:
        path (Path): The absolute path to the original file.
        dttm (str): The datetime that the original file was loaded and backed up in the format '%Y-%m-%d-%H-%M-%S'.
            Identifies a unique backup.
        file_id (str): A unique identifier for the file generated by hashing its absolute path.

    """

    def __init__(self, file_id: str, path: str):
        self.file_id = file_id
        self.path = path
        self.dttm = parse_backup_dttm(str(path))

    def restore(self, to):
        """
        Restore the file from the last backup if one exists.

        Args:
            to (str): The path to where you want to restore the file.
        """
        copy(self.path, to)

    def __repr__(self):
        return f"BackupFile(file_id={self.file_id}, path = {self.path})"


class File(BackupControl):
    """
    Provides functionality to backup files and retrieve them.

    Args:
        path (str): The path to the file that you want to back up or retrieve.

    Attributes:
        path (Path): The absolute path to the original file.
        ext (str): The file extension.
        dttm_str (str): The current date and time as a string in the format '%Y-%m-%d-%H-%M-%S'.
        file_id (str): A unique identifier for the file generated by hashing its absolute path.
        backup_dir (str): The path to the directory where backup files will be saved.
        backup_filename (str): The name of the backup file, constructed from the unique file id, the datetime it was loaded and the extension.
        backup_csv_path (str): The path to the backup CSV file where information about each backup is logged.

     Methods:
        backup(self) -> None:
            Makes a backup of the file. Backups are saved in the users Temporary Files (see `tempfile.gettempdir()` or `File.backup_dir`).

        restore(self, to:str) -> None:
            Restores the file from the last backup if one exists.

        _generate_file_id(self) -> None:
            Generates the file's unique identifier as using a hash of the absolute file path.

        _generate_file_name(self) -> None:
            Generates the name of the file, constructed from the unique file id, the datetime it was loaded and the extension.
            This allows the file to be backed up as a unique version of a particular file at a particular time.

        _make_backup(self) -> None:
            Makes a backup of the file. This function copies the file to the backup directory with a unique filename.
            It also logs a row in the backup csv file to help find a particular backup when inspecting the file system.

        list_backups(self) -> List[str]:
            Lists backed up versions of the File, ordered from newest to oldest.

    Note:
        Inherits from the BackUp class.

    Example:
        >>> file = File('path/to/my/file.txt')
        >>> file.backup()
        >>> file.restore('path/to/my/restored_file.txt')
    """

    def __init__(self, path: str | Path = "", from_json: bool = False, **args):
        # TODO: Make protected properties so they can't be manipulated
        self.path = Path(path)
        # Check  if the file exists
        if not self.path.exists():
            msg = "File not found!"
            raise OSError(msg)
        self.ext = self.path.suffix
        self.dttm_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self._generate_file_id()
        self._generate_file_name()
        super().__init__(**args)

    def __repr__(self):
        """Print method"""
        return f"Flood Modeller {self.ext} File\nPath: {self.path.__str__()}\nID: {self.file_id}"

    def _generate_file_id(self):
        """
        Generate the file's unique identifier as using a hash of the absolute file path
        """
        # hash the absolute path becuase the same file name / directroy structure may be mirrored across projects
        # TODO: Use a function that produces a shorter has to make interpretation of the directory easier
        fp_bytes = str(self.path.absolute()).encode()
        self.file_id = sha1(fp_bytes).hexdigest()

    def _generate_file_name(self) -> None:
        """
        Generate the name of the file, constructed from the unique file id, the datetime it was loaded and the extension.
        This allows the file to be backed up as a unique version of a particular file at a particular time.
        """
        self.backup_filename = self.file_id + "_" + self.dttm_str + self.ext

    def _make_backup(self) -> None:
        """
        Make a backup of the file. This function copies the file to the backup directory with a unique filename.
        It also logs a row in the backup csv file to help find a particular backup when inspecting the file system.
        """
        # Construct the path and copy the file
        backup_filepath = Path(self.backup_dir, self.backup_filename)
        copy(self.path, backup_filepath)
        # Log an entry to the csv to make it easy to find the file
        # TODO: Only log file_id and poath, don't log duplicate lines. Needs to be fast so it doesn't slow FMFile down
        log_str = f"{self.path!s},{self.file_id},{self.dttm_str}\n"
        with open(self.backup_csv_path, "a") as f:
            f.write(log_str)

    def list_backups(self) -> list:
        """
        List backed up versions of the File, ordered from newest to oldest.
        """
        backup_files = list(self.backup_dir.glob(f"{self.file_id}*"))
        backup_files.sort(reverse=True)
        if len(backup_files) <= 0:
            return []
        return [BackupFile(file_id=self.file_id, path=path) for path in backup_files]

    def backup(self) -> None:
        """
        High level method to make a backup of the file.
        This function will make a backup of a file, only if there isn't already an equivalent backup in the temporary folder.
        Backups are saved in the users Temporary Files (see `tempfile.gettempdir()` or `File.backup_dir`).
        """
        # get the backups of that file
        backups = self.list_backups()
        # If there aren't any backups then backup the file
        if len(backups) == 0 or not filecmp.cmp(self.path, backups[0].path):
            self._make_backup()
        # If the file doesn't match the last backup then do a back up
        # TODO: Use FloodModeller API implemented equivalence testing. This is implemented at a higher level than FMFile where this method is called.
        # TODO: Return the file path?

    def clear_backup(self):
        """
        Clears all backups for the file and removes entries from the logs
        """
        # Clear the backup
        super().clear_backup(file_id=self.file_id)
        # Drop the files entries from the log
        backup_logs = pd.read_csv(self.backup_csv_path)
        backup_logs = backup_logs[backup_logs.file_id != self.file_id]
        backup_logs.to_csv(self.backup_csv_path, index=False)
