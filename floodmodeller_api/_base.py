"""
Flood Modeller Python API
Copyright (C) 2022 Jacobs U.K. Limited

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty 
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details. 

You should have received a copy of the GNU General Public License along with this program.  If not, see https://www.gnu.org/licenses/.

If you have any query about this program or this License, please contact us at support@floodmodeller.com or write to the following 
address: Jacobs UK Limited, Flood Modeller, Cottons Centre, Cottons Lane, London, SE1 2QG, United Kingdom.
"""

""" Holds the base file class for API file classes """

from pathlib import Path
from .version import __version__


class FMFile:
    """Base class for all Flood Modeller File types"""

    _filetype = None
    _suffix = None

    def __init__(self):
        if self._filepath != None:
            self._filepath = Path(self._filepath).resolve()  # save filepath to class
            # Check if filepath valid
            # * Add check or fix for path lengths greater than DOS standard length of 260 characters

            if not self._filepath.suffix.lower() == self._suffix:
                raise TypeError(
                    f"Given filepath does not point to a {self._filetype} file. Please point to the full path for a {self._filetype} file"
                )
            if not self._filepath.exists():
                raise FileNotFoundError(
                    f"{self._filetype} file does not exist! If you are wanting to create a new {self._filetype}, initiate the class without a given "
                    f"filepath to create a new blank {self._filetype} or point the filepath of an existing {self._filetype} to use as a template, "
                    f"then use the .save() method to save to a new filepath"
                )

    def __repr__(self):
        return f"<floodmodeller_api Class: {self._filetype}(filepath={self._filepath})>"

    def _write(self):
        raise NotImplementedError

    def _read(self):
        raise NotImplementedError

    def _update(self):
        f"""Updates the existing {self._filetype} based on any altered attributes"""
        if self._filepath == None:
            raise UserWarning(
                f"{self._filetype} must be saved to a specific filepath before update() can be called."
            )

        string = self._write()
        with open(self._filepath, "w") as _file:
            _file.write(string)
        print(f"{self._filetype} File Updated!")

    def _save(self, filepath):
        filepath = Path(filepath).absolute()
        if not filepath.suffix.lower() == self._suffix:
            raise TypeError(
                f'Given filepath does not point to a filepath suffixed "{self._suffix}". Please point to the full path to save the {self._filetype} file'
            )

        if not filepath.parent.exists():
            Path.mkdir(filepath.parent)

        string = self._write()
        with open(filepath, "w") as _file:
            _file.write(string)
        self._filepath = filepath  # Updates the filepath attribute to the given path

        print(f"{self._filetype} File Saved to: {filepath}")

    def _handle_exception(self, err, when):
        tb = err.__traceback__
        while tb.tb_next is not None:
            tb = tb.tb_next
        line_no = tb.tb_lineno
        tb_path = Path(tb.tb_frame.f_code.co_filename)
        fname = "/".join(tb_path.parts[-2:])

        raise Exception(
            "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
            f"\nAPI Error: Problem encountered when trying to {when} {self._filetype} file {self._filepath}."
            f"\n\nDetails: {__version__}-{fname}-{line_no}"
            f"\nMsg: {err}"
            "\n\nFor additional support, go to: https://github.com/People-Places-Solutions/floodmodeller-api"
        )
