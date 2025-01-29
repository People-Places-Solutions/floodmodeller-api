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

""" Holds the base file class for API file classes """

import logging
from pathlib import Path
from typing import NoReturn

from .backup import File
from .diff import check_item_with_dataframe_equal
from .to_from_json import Jsonable
from .units._base import Unit
from .units.iic import IIC
from .urban1d._base import UrbanSubsection, UrbanUnit
from .util import FloodModellerAPIError, handle_exception


class FMFile(Jsonable):
    """Base class for all Flood Modeller File types"""

    _filetype: str
    _suffix: str
    MAX_DIFF = 25

    def __init__(self, filepath: str | Path | None = None, **kwargs):
        if filepath is not None:
            self._filepath = Path(filepath)
            # * Add check or fix for path lengths greater than DOS standard length of 260 characters

            if self._filepath.suffix.lower() != self._suffix:
                msg = f"Given filepath does not point to a {self._filetype} file. Please point to the full path for a {self._filetype} file"
                raise TypeError(msg)
            if not self._filepath.exists():
                msg = (
                    f"{self._filetype} file does not exist! If you are wanting to create a new {self._filetype}, initiate the class without a given "
                    f"filepath to create a new blank {self._filetype} or point the filepath of an existing {self._filetype} to use as a template, "
                    f"then use the .save() method to save to a new filepath"
                )
                raise FileNotFoundError(msg)
            # If the file is not a ZZN file, then perform a backup
            # This performs a conditional back up, only copying the file if an equivalent copy doesn't already exist
            if self._filetype != "ZZN":
                file = File(path=self._filepath)
                file.backup()
                # Add the file object as a property to expose the restore method
                self.file = file

    @property
    def filepath(self) -> Path:
        if not hasattr(self, "_filepath"):
            msg = "Object has no filepath."
            raise AttributeError(msg)
        return self._filepath

    @property
    def filetype(self) -> str:
        return self._filetype

    def __repr__(self):
        filepath = "<in_memory>" if not hasattr(self, "_filepath") else self._filepath
        return f"<floodmodeller_api Class: {self._filetype}(filepath={filepath})>"

    def _write(self):
        raise NotImplementedError

    def _read(self):
        raise NotImplementedError

    def _update(self):
        """Updates the existing self._filetype based on any altered attributes"""
        if self._filepath is None:
            msg = f"{self._filetype} must be saved to a specific filepath before update() can be called."
            raise UserWarning(msg)

        string = self._write()
        with open(self._filepath, "w") as _file:
            _file.write(string)
        logging.info("%s File Updated!", self._filepath)

    def _save(self, filepath):
        filepath = Path(filepath).absolute()
        if filepath.suffix.lower() != self._suffix:
            msg = f'Given filepath does not point to a filepath suffixed "{self._suffix}". Please point to the full path to save the {self._filetype} file'
            raise TypeError(msg)

        if not filepath.parent.exists():
            Path.mkdir(filepath.parent)

        string = self._write()
        with open(filepath, "w") as _file:
            _file.write(string)
        self._filepath = filepath  # Updates the filepath attribute to the given path

        logging.info("%s File Saved to: %s", self._filetype, filepath)

    @handle_exception(when="compare")
    def _diff(self, other, force_print=False) -> None:
        def _format_diff(diff_list, max_items=None) -> str:
            return "\n".join(
                f"  {name}:  {reason}"
                for name, reason in (diff_list[:max_items] if max_items else diff_list)
            )

        if self._filetype != other._filetype:
            msg = "Cannot compare objects of different filetypes"
            raise TypeError(msg)
        diff = self._get_diff(other)
        if diff[0]:
            logging.info("No difference, files are equivalent")
            return
        differences = (
            f"[Showing first {self.MAX_DIFF} differences...]\n"
            f"{_format_diff(diff[1], self.MAX_DIFF)}\n"
            "...To see full list of all differences add force_print=True"
            if len(diff[1]) > self.MAX_DIFF and not force_print
            else _format_diff(diff[1])
        )
        logging.info("Files not equivalent, %s difference(s) found:\n%s", len(diff[1]), differences)

    def _get_diff(self, other):
        return self.__eq__(other, return_diff=True)  # pylint: disable=unnecessary-dunder-call

    def _handle_exception(self, err, when) -> NoReturn:
        filepath_or_none = self._filepath if hasattr(self, "_filepath") else None
        raise FloodModellerAPIError(err, when, self._filetype, filepath_or_none) from err

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
                        ),
                    )
                    continue

        except Exception as e:
            result = False
            diff.append((f"{self._filetype}->{key}", f"Error encountered: {e.args[0]}"))

        return (result, diff) if return_diff else result
