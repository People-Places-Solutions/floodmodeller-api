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

from typing import TYPE_CHECKING, Any

from . import units
from ._base import FMFile
from .util import handle_exception

if TYPE_CHECKING:
    from pathlib import Path


class IED(FMFile):
    """Reads and write Flood Modeller event data format '.ied'
    Args:
        ied_filepath (str, optional): Full filepath to ied file. If not specified, a new IED class will be created.

    Output:
        Initiates 'IED' class object

    Raises:
        TypeError: Raised if ied_filepath does not point to a .ied file
        FileNotFoundError: Raised if ied_filepath points to a file which does not exist
    """

    _filetype: str = "IED"
    _suffix: str = ".ied"

    @handle_exception(when="read")
    def __init__(self, ied_filepath: str | Path | None = None, from_json: bool = False):
        if from_json:
            return
        if ied_filepath is not None:
            FMFile.__init__(self, ied_filepath)

            self._read()

        else:
            # No filepath specified, create new 'blank' IED in memory
            self._ied_struct: list[dict[str, Any]] = []
            self._raw_data: list[str] = []

        self._get_unit_definitions()

    def _read(self):
        # Read IED data
        with open(self._filepath) as ied_file:
            self._raw_data = [line.rstrip("\n") for line in ied_file]

        # Generate IED structure
        self._update_ied_struct()

    @handle_exception(when="write")
    def _write(self) -> str:
        """Returns string representation of the current IED data"""
        self._write_raw_data()
        self._update_ied_struct()
        self._update_unit_names()

        return "\n".join(self._raw_data) + "\n"

    def _update_unit_names(self) -> None:
        for unit_group, unit_group_name in [
            (self.boundaries, "boundaries"),
            (self.sections, "sections"),
            (self.structures, "structures"),
            (self.conduits, "conduits"),
            (self.losses, "losses"),
        ]:
            for name, unit in unit_group.copy().items():
                if name != unit.name:
                    # Check if new name already exists as a label
                    if unit.name in unit_group:
                        msg = (
                            f'Error: Cannot update label "{name}" to "{unit.name}" because '
                            f'"{unit.name}" already exists in the Network {unit_group_name} group'
                        )
                        raise Exception(msg)
                    unit_group[unit.name] = unit
                    del unit_group[name]

    def _write_raw_data(self) -> None:
        block_shift = 0
        existing_units: dict[str, list[str]] = {
            "boundaries": [],
            "structures": [],
            "sections": [],
            "conduits": [],
            "losses": [],
        }
        comment_tracker = 0
        comment_units = [unit for unit in self._all_units if unit._unit == "COMMENT"]

        for block in self._ied_struct:
            # Check for all supported boundary types
            if block["Type"] in units.SUPPORTED_UNIT_TYPES:
                unit_data = self._raw_data[
                    block["start"] + block_shift : block["end"] + 1 + block_shift
                ]
                prev_block_len = len(unit_data)

                if block["Type"] == "COMMENT":
                    comment = comment_units[comment_tracker]
                    new_unit_data = comment._write()
                    comment_tracker += 1

                else:
                    if units.SUPPORTED_UNIT_TYPES[block["Type"]]["has_subtype"]:
                        unit_name = unit_data[2][:12].strip()
                    else:
                        unit_name = unit_data[1][:12].strip()

                    # Get unit object
                    unit_group = getattr(self, units.SUPPORTED_UNIT_TYPES[block["Type"]]["group"])
                    if unit_name in unit_group:
                        # block still exists
                        new_unit_data = unit_group[unit_name]._write()
                        existing_units[units.SUPPORTED_UNIT_TYPES[block["Type"]]["group"]].append(
                            unit_name,
                        )
                    else:
                        # Bdy block has been deleted
                        new_unit_data = []

                new_block_len = len(new_unit_data)
                self._raw_data[block["start"] + block_shift : block["end"] + 1 + block_shift] = (
                    new_unit_data
                )
                # adjust block shift for change in number of lines in bdy block
                block_shift += new_block_len - prev_block_len

        # Add any new units
        for group_name, _units in existing_units.items():
            for name, unit in getattr(self, group_name).items():
                if name not in _units:
                    # Newly added unit
                    # Ensure that the 'name' attribute matches name key in boundaries
                    self._raw_data.extend(unit._write())

    def _get_unit_definitions(self):
        # Get unit definitions
        self.sections = {}
        self.boundaries = {}
        self.structures = {}
        self.conduits = {}
        self.losses = {}
        self._unsupported = {}
        self._all_units = []
        for block in self._ied_struct:
            unit_data = self._raw_data[block["start"] : block["end"] + 1]
            # Check for all supported boundary types, starting just with QTBDY type
            if block["Type"] in units.SUPPORTED_UNIT_TYPES:
                # Handle comments
                if block["Type"] == "COMMENT":
                    self._all_units.append(units.COMMENT(unit_data, n=12))
                    continue

                # Check to see whether unit type has associated subtypes so that unit name can be correctly assigned
                if units.SUPPORTED_UNIT_TYPES[block["Type"]]["has_subtype"]:
                    # Takes first 12 characters as name
                    unit_name = unit_data[2][:12].strip()
                else:
                    unit_name = unit_data[1][:12].strip()

                # Create instance of unit and add to relevant group
                unit_group = getattr(self, units.SUPPORTED_UNIT_TYPES[block["Type"]]["group"])
                if unit_name in unit_group:
                    msg = f'Duplicate label ({unit_name}) encountered within category: {units.SUPPORTED_UNIT_TYPES[block["Type"]]["group"]}'
                    raise Exception(msg)
                unit_group[unit_name] = eval(f'units.{block["Type"]}({unit_data})')

                self._all_units.append(unit_group[unit_name])

            elif block["Type"] in units.UNSUPPORTED_UNIT_TYPES:
                # Check to see whether unit type has associated subtypes so that unit name can be correctly assigned
                if units.UNSUPPORTED_UNIT_TYPES[block["Type"]]["has_subtype"]:
                    # Takes first 12 characters as name
                    unit_name = unit_data[2][:12].strip()
                    subtype = True
                else:
                    unit_name = unit_data[1][:12].strip()
                    subtype = False

                self._unsupported[f"{unit_name} ({block['Type']})"] = units.UNSUPPORTED(
                    unit_data,
                    12,
                    unit_name=unit_name,
                    unit_type=block["Type"],
                    subtype=subtype,
                )
                self._all_units.append(self._unsupported[f"{unit_name} ({block['Type']})"])

    def _update_ied_struct(self):  # noqa: C901, PLR0912
        # Generate IED structure
        ied_struct = []
        in_block = False
        bdy_block = {}
        comment_n = None
        in_comment = False

        def _finalise_block(block: dict, struct: list, end: int) -> list:
            block["end"] = end
            struct.append(block)
            return struct

        for idx, line in enumerate(self._raw_data):
            split_line = line.split(" ")

            # Deal with comment blocks explicitly as they could contain unit keywords
            if in_comment:
                if comment_n is None:
                    comment_n = int(line.strip())
                    continue

                comment_n -= 1
                if comment_n != 0:
                    continue

                ied_struct = _finalise_block(bdy_block, ied_struct, idx)
                bdy_block = {}
                in_comment = False
                in_block = False
                comment_n = None
                continue

            if line == "COMMENT":
                in_comment = True
                unit_type = line

            elif len(split_line[0]) > 1:
                if split_line[0] in units.ALL_UNIT_TYPES:
                    unit_type = split_line[0]

                elif " ".join(split_line[:2]) in units.ALL_UNIT_TYPES:
                    unit_type = " ".join(split_line[:2])

                else:
                    continue

            elif line in units.ALL_UNIT_TYPES:
                unit_type = line

            else:
                continue

            if in_block is True:
                ied_struct = _finalise_block(bdy_block, ied_struct, idx - 1)
            bdy_block = {"Type": unit_type, "start": idx}
            in_block = True

        if len(bdy_block) != 0:
            # Only adds end block if there is a bdy block present (i.e. an empty IED stays empty)
            # add ending index for final block
            ied_struct = _finalise_block(bdy_block, ied_struct, len(self._raw_data) - 1)

        self._ied_struct = ied_struct

    def diff(self, other: IED, force_print: bool = False) -> None:
        """Compares the IED class against another IED class to check whether they are
        equivalent, or if not, what the differences are. Two instances of an IED class are
        deemed equivalent if all of their attributes are equal except for the filepath and
        raw data. For example, two IED files from different filepaths that had the same
        data except maybe some differences in decimal places and some default parameters
        ommitted, would be classed as equaivalent as they would produce the same IED instance
        and write the exact same data.

        The result is printed to the console. If you need to access the returned data, use
        the method ``IED._get_diff()``

        Args:
            other (floodmodeller_api.IED): Other instance of an IED class
            force_print (bool): Forces the API to print every difference found, rather than
                just the first 25 differences. Defaults to False.
        """
        self._diff(other, force_print=force_print)

    def update(self) -> None:
        """Updates the existing IED based on any altered attributes"""

        self._update()

    def save(self, filepath: str | Path) -> None:
        """Saves the IED to the given location, if pointing to an existing file it will be overwritten.
        Once saved, the IED() class will continue working from the saved location, therefore any further calls to IED.update() will update in the latest saved location
        rather than the original source IED used to construct the class"""

        self._save(filepath)
