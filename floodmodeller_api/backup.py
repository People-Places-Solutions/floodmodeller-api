import tempfile
import os 
from hashlib import sha1
import glob
import filecmp
from pathlib import Path
from shutil import copy
from datetime import datetime
import csv


class File():
    def __init__(self, path:str):
        self.path = Path(path)
        self.ext = self.path.suffix
        self.dttm_str = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        self._generate_file_id()
        self._generate_file_name()
    
    def _generate_file_id(self):
        # hash the absolute path becuase the same file name / directroy structure may be mirrored across projects
        fp_bytes = self.path.absolute().__str__().encode()
        self.file_id = sha1(fp_bytes).hexdigest()
    
    def _generate_file_name(self):
        self.backup_filename = self.file_id + "_" + self.dttm_str + self.ext
    


class BackUp():
    """
    Class to handle file backups, and manipulation of the backup directory
    """
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.backup_dirname = "floodmodeller_api_backup"
        self.backup_dir = os.path.join(self.temp_dir, self.backup_dirname)
        self.backup_csv_path = f"{self.backup_dir}/file-backups.csv"
        self._init_backup()

    def _init_backup(self):
        dir_exists = os.path.exists(self.backup_dir)
        if not(dir_exists):
            # Create the backup directory
            os.mkdir(self.backup_dir)
        csv_exists = os.path.exists(self.backup_csv_path)
        if not(csv_exists):
            # Add a csv file to identify backups
            # A line will be added to this each time a file is backed up with the path, id and datetime
            with open(self.backup_csv_path, "x") as f:
                f.write("path,file_id,dttm\n")
    
    def clear_backup(self):
        files = glob.glob(f"{self.backup_dir}\\*")
        for f in files:
            os.remove(f)
    
    def _get_backups(self, file:File):
        backup_files = glob.glob(f"{self.backup_dir}\\{file.file_id}*")
        backup_files.sort(reverse = True)
        return backup_files
    
    def _copy_file(self, filepath, dest_file):
        file = File(filepath)
        copy(file.path, dest_file)
        log_str = f"{file.path.__str__()},{file.file_id},{file.dttm_str}\n"
        with open(self.backup_csv_path, "a") as f:
                f.write(log_str)

    def backup(self, filepath):
        file = File(filepath)
        # get the backups of that file
        backups = self._get_backups(file)
        # Generate the filepath for the backup file
        dest_file = os.path.join(self.backup_dir, file.backup_filename)
        # If there aren't any backups then backup the file
        if len(backups) == 0:
            self._copy_file(file, dest_file)
        # If the file doesn't match the last backup then do a back up
        elif not(filecmp.cmp(file.path, backups[0])):
            self._copy_file(file, dest_file)
    
    def restore(self, filepath, restore_to):
        file = File(filepath)
        backups = self._get_backups(file)
        try: 
            copy(backups[0], restore_to)
        except IndexError:
            print("This file does not have a backup")
