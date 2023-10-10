"""
Flood Modeller Python API
Copyright (C) 2023 Jacobs U.K. Limited

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
from typing import Optional, Union

from .backup import File
from .diff import check_item_with_dataframe_equal
from .units._base import Unit
from .units.iic import IIC
from .urban1d._base import UrbanSubsection, UrbanUnit
from .version import __version__


class FMFile:
    """Base class for all Flood Modeller File types"""

    _filetype: Optional[str] = None
    _suffix: Optional[str] = None

    def __init__(self, filepath: Optional[Union[str, Path]]):
        if filepath is not None:
            self._filepath = Path(filepath).resolve()  # save filepath to class
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
            # If the file is not a ZZN file, then perform a backup
            # This performs a conditional back up, only copying the file if an equivalent copy doesn't already exist
            if not self._filetype == "ZZN":
                file = File(path=self._filepath)
                file.backup()
                # Add the file object as a property to expose the restore method
                self.file = file

    def __repr__(self):
        return f"<floodmodeller_api Class: {self._filetype}(filepath={self._filepath})>"

    def _write(self):
        raise NotImplementedError

    def _read(self):
        raise NotImplementedError

    def _update(self):
        f"""Updates the existing {self._filetype} based on any altered attributes"""
        if self._filepath is None:
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

    def _diff(self, other, force_print=False):
        try:
            if self._filetype != other._filetype:
                raise TypeError("Cannot compare objects of different filetypes")
            diff = self._get_diff(other)
            if diff[0]:
                print("No difference, files are equivalent")
            else:
                print(f"Files not equivalent, {len(diff[1])} difference(s) found:")
                if len(diff[1]) > 25 and not force_print:
                    print("[Showing first 25 differences...] ")
                    print("\n".join([f"  {name}:  {reason}" for name, reason in diff[1][:25]]))
                    print("\n...To see full list of all differences add force_print=True")
                else:
                    print("\n".join([f"  {name}:  {reason}" for name, reason in diff[1]]))
        except Exception as e:
            self._handle_exception(e, when="compare")

    def _get_diff(self, other):
        return self.__eq__(other, return_diff=True)

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

    def __eq__(self, other, return_diff=False):
        result = True
        diff = []
        try:
            for key, item in self.__dict__.items():
                try:
                    if key in (
                        "_filepath",
                        "_raw_data",
                        "_gxy_filepath",
                        "_gxy_data",
                        "_xmltree",
                        "_xsd",
                        "_xsdschema",
                        "file",
                        "_log_path",
                    ):
                        continue
                    else:
                        _result, diff = check_item_with_dataframe_equal(
                            item,
                            other.__dict__[key],
                            name=f"{self._filetype}->{key}",
                            diff=diff,
                            special_types=(Unit, IIC, UrbanUnit, UrbanSubsection),
                        )
                        if not _result:
                            result = False
                except KeyError as ke:
                    result = False
                    diff.append(
                        (
                            f"{self._filetype}->{key}",
                            f"Key: '{ke.args[0]}' missing in other",
                        )
                    )
                    continue

        except Exception as e:
            result = False
            diff.append((f"{self._filetype}->{key}", f"Error encountered: {e.args[0]}"))

        return (result, diff) if return_diff else result
