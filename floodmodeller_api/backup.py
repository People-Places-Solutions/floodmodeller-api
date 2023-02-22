import tempfile
import os 
from hashlib import sha1
import glob
import filecmp
from pathlib import Path
from shutil import copy
from datetime import datetime




class BackUp():
    # TODO: Finish docs here
    """Controls set up and clearing of file backups.

    Args:
        N/A

    Output:
        Initiates 'BackUp' class object

    Raises:
        N/A
    """
    def __init__(self):
        # TODO: Make these protected properties so it is difficult for a user to overwrite them and then run clear_backup to clear the wrong directory
        self.temp_dir = tempfile.gettempdir()
        self.backup_dirname = "floodmodeller_api_backup"
        self.backup_dir = os.path.join(self.temp_dir, self.backup_dirname)
        self.backup_csv_path = f"{self.backup_dir}/file-backups.csv"
        self._init_backup()

    def _init_backup(self):
        """
        Initialise the back up directory and create a csv file for logging backup information. 
        """
        # Backup Directory
        dir_exists = os.path.exists(self.backup_dir)
        if not(dir_exists):
            # Create the backup directory
            os.mkdir(self.backup_dir)
        # Backup CSV
        csv_exists = os.path.exists(self.backup_csv_path)
        if not(csv_exists):
            # Add a csv file to identify backups
            # A line will be added to this each time a file is backed up with the path, id and datetime
            # TODO: Only log path and file ID - don't add duplicate rows
            with open(self.backup_csv_path, "x") as f:
                f.write("path,file_id,dttm\n")

    def clear_backup(self):
        """
        Remove all of the backup files in the backup directory
        """
        files = glob.glob(f"{self.backup_dir}\\*")
        for f in files:
            os.remove(f)
    
    

class File(BackUp):
    """
    Provides functionality to backup files and retrieve them.

    Args:
        path: str
            The path to the file that you either want to back up or retrieve.
    
    Output:
        Initiates a 'File' object
    """
    def __init__(self, path:str, **args):
        # TODO: Check file exists
        # TODO: Make protected properties so they can't be manipulated
        self.path = Path(path)
        self.ext = self.path.suffix
        self.dttm_str = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
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
        fp_bytes = self.path.absolute().__str__().encode()
        self.file_id = sha1(fp_bytes).hexdigest()
    
    def _generate_file_name(self) -> None:
        """"
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
        backup_filepath = os.path.join(self.backup_dir, self.backup_filename)
        copy(self.path, backup_filepath)
        # Log an entry to the csv to make it easy to find the file
        # TODO: Only log file_id and poath, don't log duplicate lines. Needs to be fast so it doesn't slow FMFile down
        log_str = f"{self.path.__str__()},{self.file_id},{self.dttm_str}\n"
        with open(self.backup_csv_path, "a") as f:
                f.write(log_str)
    
    def _list_backups(self) -> list:
        """
        List backed up versions of the File, ordered from newest to oldest.
        """
        # TODO: Add some functionality to this to parse the datetimes and generate a dataframe of backups
        # That would allow other methods to print useful info and retrieve specific backups based upon date
        backup_files = glob.glob(f"{self.backup_dir}\\{self.file_id}*")
        backup_files.sort(reverse = True)
        return backup_files

    def backup(self) -> None:
        """
        High level method to make a backup of the file. 
        This function will make a backup of a file, only if there isn't already an equivalent backup in the temporary folder. 
        Backups are saved in the users Temporary Files (see `tempfile.gettempdir()` or `File.backup_dir`).
        """
        # get the backups of that file
        backups = self._list_backups()
        # Generate the filepath for the backup file
        dest_file = os.path.join(self.backup_dir, self.backup_filename)
        # If there aren't any backups then backup the file
        if len(backups) == 0:
            self._make_backup()
        # If the file doesn't match the last backup then do a back up
        # TODO: Use FloodModeller API implemented equivalence testing. This is implemented at a higher level than FMFile where this method is called.
        elif not(filecmp.cmp(self.path, backups[0])):
            self._make_backup()
        # TODO: Return the file path?
    
    def restore(self, to:str):
        """
        Restore the file from a backup. This 

        Args:
            to (str): The path to where you want to restore the file.
        """
        backups = self._list_backups()
        try: 
            copy(backups[0], to)
        # TODO: Implement something better than this if the file doesn't exist
        except IndexError:
            print("This file does not have a backup")