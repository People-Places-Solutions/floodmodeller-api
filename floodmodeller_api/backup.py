import tempfile
import os 
from hashlib import sha1
import glob
import filecmp
from pathlib import Path
from shutil import copy
from datetime import datetime

class File():
    def __init__(self, path:str):
        self.path = Path(path)
        self.ext = self.path.suffix
        self.generate_file_id()
        self.generate_file_name()
    
    def generate_file_id(self):
        # hash the absolute path becuase the same file name / directroy structure may be mirrored across projects
        fp_bytes = self.path.absolute().__str__().encode()
        self.file_id = sha1(fp_bytes).hexdigest()
    
    def generate_file_name(self):
        dttm_str = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        self.backup_filename = self.file_id + "_" + dttm_str + self.ext
    


class BackUp():
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.backup_dirname = "floodmodeller_api_backup"
        self.backup_dir = os.path.join(self.temp_dir, self.backup_dirname)
        self.init_backup()

    def init_backup(self):
        dir_exists = os.path.exists(self.backup_dir)
        if not(dir_exists):
            os.mkdir(self.backup_dir)
    
    def remove_backup_dir(self):
        os.rmdir(self.backup_dir)
    
    def clear_backup_dir(self):
        files = glob.glob(f"{self.backup_dir}\\*")
        for f in files:
            os.remove(f)
    
    def get_backups(self, file:File):
        backup_files = glob.glob(f"{self.backup_dir}\\{file.file_id}*")
        backup_files.sort(reverse = True)
        return backup_files

    def backup_file(self, file:File):
        # get the backups of that file
        backups = self.get_backups(file)
        # Generate the filepath for the backup file
        dest_file = os.path.join(self.backup_dir, file.backup_filename)
        # If there aren't any backups then backup the file
        if len(backups) == 0:
            copy(file.path, dest_file)
        # If the file doesn't match the last backup then do a back up
        elif not(filecmp.cmp(file.path, backups[0])):
            copy(file.path, dest_file)
        else:
            # otherwise do nothing
            print("Backup Exists")


#file = File("test/test_data/EX2.DAT")
#backup = BackUp()

#backup.backup_file(file)

# backup.clear_backup_dir()
