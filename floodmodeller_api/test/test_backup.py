from pathlib import Path

import pandas as pd
import pytest

from floodmodeller_api.backup import BackupControl, File


@pytest.fixture()
def backup_control():
    # Use a different directory for testing
    return BackupControl()


@pytest.fixture()
def file(test_workspace):
    test_file = Path(test_workspace, "EX1.DAT")
    file = File(test_file)
    # Make a backup to clear in test
    file.backup()
    return file


def test_init_backup(backup_control):
    """Has the backup been initialised correctly?"""
    assert backup_control.backup_dir.exists()
    assert backup_control.backup_csv_path.exists()


def test_generate_file_id(file, test_workspace):
    """Does this generate a consistent file ID for the same file on disk?"""
    # Test that the file ID is the same for the same path input
    file1 = File(Path(test_workspace, "EX1.DAT"))
    file2 = File(Path(test_workspace, "EX1.DAT"))
    assert file1.file_id == file2.file_id


def test_clear_backup(file, test_workspace):
    """
    Does the the clear_backup method work correctly
    """
    # Clearing backup -------------------
    # Load a different file to check it isn't affected by the
    other_file = File(Path(test_workspace, "EX3.DAT"))
    # Assert there is a backup for the other file
    other_file.backup()
    # Clear the backups for the file to test backup functionality
    file.clear_backup()
    # Assert that clearing the backup has worked - there aren't any backups for the file
    assert len(file.list_backups()) == 0
    # And that clearing it hasn't affected backups for the other file
    assert len(other_file.list_backups()) > 0


def test_backup_locations(file):
    """
    Does it make a backup in the right place?
    """
    # Making a backup --------------------
    file.clear_backup()
    # make a backup and check if file exists
    file.backup()
    backup_file_path = Path(file.backup_dir, file.backup_filename)
    assert backup_file_path.exists()
    # check if contents of backup file match the original file
    with open(backup_file_path) as f1, open(file.path) as f2:
        assert f1.read() == f2.read()


def test_no_duplicate_backup(file, test_workspace):
    """The backup method should only backup if the file has changed"""
    # Don't Make Duplicate -------------------
    # Check that the file isn't backed up again if it hasn't changed
    the_same_file = File(Path(test_workspace, "EX1.DAT"))
    # Append something to the dttm string to ensure the filename is different to the previous backup
    # If the two File objects are created in the same second then then will have identical file names
    # The function should check for equivalence between file contents.
    the_same_file.dttm_str = the_same_file.dttm_str + "_1"
    # Generate a new file name
    the_same_file._generate_file_name()
    # Attempt a backup
    the_same_file.backup()
    # Check that the file hasn't been created
    duplicate_backup_path = Path(the_same_file.backup_dir, the_same_file.backup_filename)
    assert not duplicate_backup_path.exists()


def test_backup_logs(file):
    """Are backups being logged in the CSV?"""
    # Clear the backup
    file.clear_backup()
    # There shouldn't be any edits in the csv
    backup_logs = pd.read_csv(file.backup_csv_path)
    backup_count = backup_logs[
        (backup_logs.file_id == file.file_id) & (backup_logs.dttm == file.dttm_str)
    ].shape[0]
    assert backup_count == 0
    # Make a backup and assert it is in the CSV
    file.backup()
    # Check edits to the backup CSV
    # Check a row has been added to the csv for the file & version
    backup_logs = pd.read_csv(file.backup_csv_path)
    backup_count = backup_logs[
        (backup_logs.file_id == file.file_id) & (backup_logs.dttm == file.dttm_str)
    ].shape[0]
    assert backup_count == 1


def test_list_backups(file):
    """Does the list backups method work correctly?"""
    # First clear any backups that exist
    file.clear_backup()
    # make a backup and check if it appears in the backup list
    file.backup()
    backups = file.list_backups()
    expected_backup = Path(file.backup_dir, file.backup_filename)
    assert expected_backup in [backup.path for backup in backups]
