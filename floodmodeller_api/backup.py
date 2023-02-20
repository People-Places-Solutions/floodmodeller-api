import tempfile
import os 
from hashlib import sha1
import glob
import filecmp
from pathlib import Path
from shutil import copy
from datetime import datetime




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
    
    

class File(BackUp):
    def __init__(self, path:str, **args):
        self.path = Path(path)
        self.ext = self.path.suffix
        self.dttm_str = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        self._generate_file_id()
        self._generate_file_name()
        super().__init__(**args)

    def __repr__(self): 
        return f"Flood Modeller {self.ext} File\nPath: {self.path.__str__()}\nID: {self.file_id}"
    
    def _generate_file_id(self):
        # hash the absolute path becuase the same file name / directroy structure may be mirrored across projects
        fp_bytes = self.path.absolute().__str__().encode()
        self.file_id = sha1(fp_bytes).hexdigest()
    
    def _generate_file_name(self):
        self.backup_filename = self.file_id + "_" + self.dttm_str + self.ext
    
    def _make_backup(self):
        # Construct the path and copy the file
        backup_filepath = os.path.join(self.backup_dir, self.backup_filename)
        copy(self.path, backup_filepath)
        # Log an entry to the csv to make it easy to find the file
        log_str = f"{self.path.__str__()},{self.file_id},{self.dttm_str}\n"
        with open(self.backup_csv_path, "a") as f:
                f.write(log_str)
    def _list_backups(self):
        # TODO: Add some functionality to this to parse the datetimes and generate a dataframe of backups
        # That would allow other methods to print useful info and retrieve specific backups based upon date
        backup_files = glob.glob(f"{self.backup_dir}\\{self.file_id}*")
        backup_files.sort(reverse = True)
        return backup_files

    def backup(self):
        # get the backups of that file
        backups = self._list_backups()
        # Generate the filepath for the backup file
        dest_file = os.path.join(self.backup_dir, self.backup_filename)
        # If there aren't any backups then backup the file
        if len(backups) == 0:
            self._make_backup()
        # If the file doesn't match the last backup then do a back up
        elif not(filecmp.cmp(self.path, backups[0])):
            self._make_backup()
    
    def restore(self, to):
        backups = self._list_backups()
        try: 
            copy(backups[0], to)
        except IndexError:
            print("This file does not have a backup")