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

from pathlib import Path
from typing import Any

from . import units
from ._base import FMFile
from .units._base import Unit
from .units._helpers import join_10_char, split_10_char, to_float, to_int
from .util import handle_exception
from .validation.validation import _validate_unit


class DAT(FMFile):
    """Reads and write Flood Modeller datafile format '.dat'

    Args:
        dat_filepath (str, optional): Full filepath to dat file. If not specified, a new DAT class will be created. Defaults to None.

    Output:
        Initiates 'DAT' class object

    Raises:
        TypeError: Raised if dat_filepath does not point to a .dat file
        FileNotFoundError: Raised if dat_filepath points to a file which does not exist
    """

    _filetype: str = "DAT"
    _suffix: str = ".dat"

    @handle_exception(when="read")
    def __init__(
        self,
        dat_filepath: str | Path | None = None,
        with_gxy: bool = False,
        from_json: bool = False,
    ) -> None:
        if from_json:
            return
        if dat_filepath is not None:
            FMFile.__init__(self, dat_filepath)
            self._read()

        else:
            self._create_from_blank(with_gxy)

        self._get_general_parameters()
        self._get_unit_definitions()

    def update(self) -> None:
        """Updates the existing DAT based on any altered attributes"""
        self._update()
        self._write_gxy(self._gxy_filepath)

    def save(self, filepath: str | Path) -> None:
        """Saves the DAT to the given location, if pointing to an existing file it will be overwritten.
        Once saved, the DAT() class will continue working from the saved location, therefore any further calls to DAT.update() will
        update in the latest saved location rather than the original source DAT used to construct the class

        Args:
            filepath (str): Filepath to new save location including the name and '.dat' extension

        Raises:
            TypeError: Raised if given filepath doesn't point to a file suffixed '.dat'
        """
        filepath = Path(filepath).absolute()
        self._save(filepath)
        self._write_gxy(filepath)

    def _write_gxy(self, filepath):
        if self._gxy_data is not None:
            gxy_string = self._gxy_data
            new_gxy_path = filepath.with_suffix(".gxy")
            with open(new_gxy_path, "w") as gxy_file:
                gxy_file.write(gxy_string)
            self._gxy_filepath = new_gxy_path

    def diff(self, other: DAT, force_print: bool = False) -> None:
        """Compares the DAT class against another DAT class to check whether they are
        equivalent, or if not, what the differences are. Two instances of a DAT class are
        deemed equivalent if all of their attributes are equal except for the filepath and
        raw data. For example, two DAT files from different filepaths that had the same
        data except maybe some differences in decimal places and some default parameters
        ommitted, would be classed as equivalent as they would produce the same DAT instance
        and write the exact same data.

        The result is printed to the console. If you need to access the returned data, use
        the method ``DAT._get_diff()``

        Args:
            other (floodmodeller_api.DAT): Other instance of a DAT class
            force_print (bool): Forces the API to print every difference found, rather than
                just the first 25 differences. Defaults to False.
        """
        self._diff(other, force_print=force_print)

    # def _get_unit_from_connectivity(self, method) #use this as method prev and next

    @handle_exception(when="calculate next unit in")
    def next(self, unit: Unit) -> Unit | list[Unit] | None:
        """Finds next unit in the reach.

        Next unit in reach can be infered by:
            The next unit in the .dat file structure - such as when a river section has a positive distance to next
            The units with the exact same name - such as a junction unit
            The next unit as described in the ds_label - such as with Bridge units

        Args:
            unit (Unit): flood modeller unit input.

        Returns:
            Union[Unit, list[Unit], None]: Flood modeller unit either on its own or in a list if more than one follows in reach.
        """
        # Needs to handle same name match outside dist to next (e.g. inflow)
        if hasattr(unit, "dist_to_next"):
            # Case 1a - positive distance to next
            if unit.dist_to_next != 0:
                return self._next_in_dat_struct(unit)

            # Case 1b - distance to next = 0
            return self._name_label_match(unit)

        # Case 2: next unit is in ds_label
        if hasattr(unit, "ds_label"):
            return self._name_label_match(unit, name_override=unit.ds_label)

        if unit._unit == "JUNCTION":
            return [self._name_label_match(unit, name_override=lbl) for lbl in unit.labels]  # type: ignore[misc, attr-defined]

        if unit._unit in ("QHBDY", "NCDBDY", "TIDBDY"):
            return None

        return self._name_label_match(unit)

    @handle_exception(when="calculate previous unit in")
    def prev(self, unit: Unit) -> Unit | list[Unit] | None:
        """Finds previous unit in the reach.

        Previous unit in reach can be infered by:
            The previous unit in the .dat file structure - such as when the previous river section has a positive distance to next.
            The units with the exact same name - such as a junction unit
            The previous unit as linked through upstream and downstream labels - such as with Bridge units

        Args:
            unit (Unit): flood modeller unit input.

        Returns:
            Union[Unit, list[Unit], None]: Flood modeller unit either on its own or in a list if more than one follows in reach.
        """
        # Case 1: Unit is input boundary condition
        if unit._unit in (
            "QTBDY",
            "HTBDY",
            "REFHBDY",
            "FEHBDY",
            "FRQSIM",
            "FSRBDY",
            "FSSR16BDY",
            "GERRBDY",
            "REBDY",
            "REFH2BDY",
            "SCSBDY",
        ):
            return None

        if unit._unit == "JUNCTION":
            return [self._name_label_match(unit, name_override=lbl) for lbl in unit.labels]  # type: ignore[misc, attr-defined]

        prev_units = []
        _prev_in_dat = self._prev_in_dat_struct(unit)
        _name_match = self._name_label_match(unit)
        _ds_label_match = self._ds_label_match(unit)
        _junction_match = [
            junction
            for junction in self._all_units
            if junction._unit == "JUNCTION" and unit.name in junction.labels
        ]

        # Case 2: Previous unit has positive distance to next
        if (
            _prev_in_dat
            and hasattr(_prev_in_dat, "dist_to_next")
            and _prev_in_dat.dist_to_next != 0
        ):
            prev_units.append(_prev_in_dat)
            _name_match = None  # Name match does apply if upstream section exists

        # All other matches added (matching name, matching name to ds_label and junciton)
        for match in [_name_match, _ds_label_match, _junction_match]:
            if isinstance(match, list):
                prev_units.extend(match)
            elif match:
                prev_units.append(match)

        if len(prev_units) == 0:
            return None
        if len(prev_units) == 1:
            return prev_units[0]
        return prev_units

    def _next_in_dat_struct(self, current_unit: Unit) -> Unit | None:
        """Finds next unit in the dat file using the index position.

        Returns:
            Unit with all associated data
        """

        for idx, unit in enumerate(self._all_units):
            # Names checked first to speed up comparison
            if unit.name == current_unit.name and unit == current_unit:
                try:
                    return self._all_units[idx + 1]
                except IndexError:
                    return None

        return None

    def _prev_in_dat_struct(self, current_unit: Unit) -> Unit | None:
        """Finds previous unit in the dat file using the index position.

        Returns:
            Unit with all associated data
        """
        for idx, unit in enumerate(self._all_units):
            # Names checked first to speed up comparison
            if unit.name == current_unit.name and unit == current_unit:
                if idx == 0:
                    return None
                return self._all_units[idx - 1]

        return None

    def _ds_label_match(self, current_unit: Unit) -> Unit | list[Unit] | None:
        """Pulls out all units with ds label that matches the input unit.

        Returns:
            Union[Unit, list[Unit], None]: Either a singular unit or list of units with ds_label matching, if none exist returns none.
        """

        _ds_list = [
            item
            for item in self._all_units
            if hasattr(item, "ds_label") and item.ds_label == current_unit.name
        ]

        if len(_ds_list) == 0:
            return None
        if len(_ds_list) == 1:
            return _ds_list[0]
        return _ds_list

    def _name_label_match(
        self,
        current_unit: Unit,
        name_override: str | None = None,
    ) -> Unit | list[Unit] | None:
        """Pulls out all units with same name as the input unit.

        Returns:
            Union[Unit, list[Unit], None]: Either a singular unit or list of units with matching names, if none exist returns none. Does not return itself
        """

        _name = name_override or str(current_unit.name)
        _name_list = []
        for item in self._all_units:
            if item.name == _name and item != current_unit:
                _name_list.append(item)
            else:
                pass

        if len(_name_list) == 0:
            return None
        if len(_name_list) == 1:
            return _name_list[0]
        return _name_list

    def _read(self) -> None:
        # Read DAT data
        with open(self._filepath) as dat_file:
            self._raw_data: list[str] = [line.rstrip("\n") for line in dat_file]

        # Generate DAT structure
        self._update_dat_struct()

        # Get network .gxy if present
        gxy_path = self._filepath.with_suffix(".gxy")
        if gxy_path.exists():
            self._gxy_filepath = gxy_path
            with open(self._gxy_filepath) as gxy_file:
                self._gxy_data: str | None = gxy_file.read()
        else:
            self._gxy_filepath = None
            self._gxy_data = None

    @handle_exception(when="write")
    def _write(self) -> str:
        """Returns string representation of the current DAT data

        Returns:
            str: Full string representation of DAT in its most recent state (including changes not yet saved to disk)
        """
        self._update_raw_data()
        self._update_general_parameters()
        self._update_dat_struct()
        self._update_unit_names()

        return "\n".join(self._raw_data) + "\n"

    def _create_from_blank(self, with_gxy: bool = False) -> None:
        # No filepath specified, create new 'blank' DAT in memory
        # ** Update these to have minimal data needed (general header, empty IC header)
        self._dat_struct: list[dict[str, Any]] = [
            {"start": 0, "Type": "GENERAL", "end": 6},
            {"Type": "INITIAL CONDITIONS", "start": 7, "end": 8},
        ]
        self._raw_data = [
            "",
            "#REVISION#1",
            "         0     0.750     0.900     0.100     0.001        12SI",
            "    10.000     0.010     0.010     0.700     0.100     0.700     0.000",
            "RAD FILE",
            "",
            "END GENERAL",
            "INITIAL CONDITIONS",
            " label   ?      flow     stage froude no  velocity     umode    ustate         z",
        ]

        self._gxy_filepath = None
        if with_gxy:
            self._gxy_data = ""
        else:
            self._gxy_data = None

    def _get_general_parameters(self) -> None:
        # ** Get general parameters here
        self.title = self._raw_data[0]
        self.general_parameters = {}
        line = f"{self._raw_data[2]:<70}"
        params = split_10_char(line)
        if params[6] == "":
            # Adds the measurements unit as DEFAULT if not specified
            params[6] = "DEFAULT"
        line = f"{self._raw_data[3]:<70}"
        params.extend(split_10_char(line))

        self.general_parameters["Node Count"] = to_int(params[0], 0)
        self.general_parameters["Lower Froude"] = to_float(params[1], 0.75)
        self.general_parameters["Upper Froude"] = to_float(params[2], 0.9)
        self.general_parameters["Min Depth"] = to_float(params[3], 0.1)
        self.general_parameters["Convergence Direct"] = to_float(params[4], 0.001)
        self._label_len = to_int(params[5], 12)  # label length
        self.general_parameters["Units"] = params[6]  # "DEFAULT" set during read above.
        self.general_parameters["Water Temperature"] = to_float(params[7], 10.0)
        self.general_parameters["Convergence Flow"] = to_float(params[8], 0.01)
        self.general_parameters["Convergence Head"] = to_float(params[9], 0.01)
        self.general_parameters["Mathematical Damping"] = to_float(params[10], 0.7)
        self.general_parameters["Pivotal Choice"] = to_float(params[11], 0.1)
        self.general_parameters["Under-relaxation"] = to_float(params[12], 0.7)
        self.general_parameters["Matrix Dummy"] = to_float(params[13], 0.0)
        self.general_parameters["RAD File"] = self._raw_data[5]  # No default, optional

    def _update_general_parameters(self) -> None:
        self._raw_data[0] = self.title
        self._raw_data[5] = self.general_parameters["RAD File"]
        general_params_1 = join_10_char(
            self.general_parameters["Node Count"],
            self.general_parameters["Lower Froude"],
            self.general_parameters["Upper Froude"],
            self.general_parameters["Min Depth"],
            self.general_parameters["Convergence Direct"],
            self._label_len,
        )
        general_params_1 += self.general_parameters["Units"]
        self._raw_data[2] = general_params_1

        general_params_2 = join_10_char(
            self.general_parameters["Water Temperature"],
            self.general_parameters["Convergence Flow"],
            self.general_parameters["Convergence Head"],
            self.general_parameters["Mathematical Damping"],
            self.general_parameters["Pivotal Choice"],
            self.general_parameters["Under-relaxation"],
            self.general_parameters["Matrix Dummy"],
        )
        self._raw_data[3] = general_params_2

    def _update_unit_names(self):
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
                        msg = f'Error: Cannot update label "{name}" to "{unit.name}" because "{unit.name}" already exists in the Network {unit_group_name} group'
                        raise Exception(msg)
                    unit_group[unit.name] = unit
                    del unit_group[name]
                    # Update label in ICs
                    if unit_group_name not in ["boundaries", "losses"]:
                        self.initial_conditions.update_label(name, unit.name)

                    # Update label in GISINFO and GXY data
                    self._update_gisinfo_label(
                        unit._unit,
                        unit._subtype,
                        name,
                        unit.name,
                        unit_group_name
                        in ["boundaries", "losses"],  # if True it ignores second lbl
                    )
                    self._update_gxy_label(unit._unit, unit._subtype, name, unit.name)

        # Update IC table names in raw_data if any name changes
        ic_start, ic_end = next(
            (unit["start"], unit["end"])
            for unit in self._dat_struct
            if unit["Type"] == "INITIAL CONDITIONS"
        )
        self._raw_data[ic_start : ic_end + 1] = self.initial_conditions._write()

    def _update_raw_data(self):
        block_shift = 0
        comment_tracker = 0
        comment_units = [unit for unit in self._all_units if unit._unit == "COMMENT"]
        prev_block_end = self._dat_struct[0]["end"]
        existing_units = {
            "boundaries": [],
            "structures": [],
            "sections": [],
            "conduits": [],
            "losses": [],
        }

        for block in self._dat_struct:
            # Check for all supported boundary types
            if block["Type"] in units.SUPPORTED_UNIT_TYPES:
                # clause for when unit has been inserted into the dat file
                if "new_insert" in block:
                    block["start"] = prev_block_end + 1
                    block["end"] = block["start"] + len(block["new_insert"]) - 1
                    self._raw_data[block["start"] : block["start"]] = block["new_insert"]
                    block_shift += len(block["new_insert"])
                    prev_block_end = block["end"]
                    del block["new_insert"]

                else:
                    unit_data = self._raw_data[
                        block["start"] + block_shift : block["end"] + 1 + block_shift
                    ]
                    prev_block_len = len(unit_data)

                    if block["Type"] == "INITIAL CONDITIONS":
                        new_unit_data = self.initial_conditions._write()
                    elif block["Type"] == "COMMENT":
                        comment = comment_units[comment_tracker]
                        new_unit_data = comment._write()
                        comment_tracker += 1

                    elif block["Type"] == "VARIABLES":
                        new_unit_data = self.variables._write()

                    else:
                        if units.SUPPORTED_UNIT_TYPES[block["Type"]]["has_subtype"]:
                            unit_name = unit_data[2][: self._label_len].strip()
                        else:
                            unit_name = unit_data[1][: self._label_len].strip()

                        # Get unit object
                        unit_group = getattr(
                            self,
                            units.SUPPORTED_UNIT_TYPES[block["Type"]]["group"],
                        )
                        if unit_name in unit_group:
                            # block still exists
                            new_unit_data = unit_group[unit_name]._write()
                            existing_units[
                                units.SUPPORTED_UNIT_TYPES[block["Type"]]["group"]
                            ].append(unit_name)
                        else:
                            # Bdy block has been deleted
                            new_unit_data = []

                    new_block_len = len(new_unit_data)
                    self._raw_data[
                        block["start"] + block_shift : block["end"] + 1 + block_shift
                    ] = new_unit_data
                    # adjust block shift for change in number of lines in bdy block
                    block_shift += new_block_len - prev_block_len
                    prev_block_end = (
                        block["end"] + block_shift
                    )  # add in to keep a record of the last block read in

    def _get_unit_definitions(self):
        self._initialize_collections()
        for block in self._dat_struct:
            unit_data = self._raw_data[block["start"] : block["end"] + 1]
            unit_type = block["Type"]

            if unit_type in units.SUPPORTED_UNIT_TYPES:
                self._process_supported_unit(unit_type, unit_data)
            elif unit_type in units.UNSUPPORTED_UNIT_TYPES:
                self._process_unsupported_unit(unit_type, unit_data)
            elif unit_type not in ("GENERAL", "GISINFO"):
                msg = f"Unexpected unit type encountered: {unit_type}"
                raise Exception(msg)

    def _initialize_collections(self):
        # Initialize unit collections
        self.sections = {}
        self.boundaries = {}
        self.structures = {}
        self.conduits = {}
        self.losses = {}
        self._unsupported = {}
        self._all_units = []

    def _process_supported_unit(self, unit_type, unit_data):
        # Handle initial conditions block
        if unit_type == "INITIAL CONDITIONS":
            self.initial_conditions = units.IIC(unit_data, n=self._label_len)
        elif unit_type == "COMMENT":
            self._all_units.append(units.COMMENT(unit_data, n=self._label_len))
        elif unit_type == "VARIABLES":
            self.variables = units.Variables(unit_data)
        else:
            # Check to see whether unit type has associated subtypes so that unit name can be correctly assigned
            unit_name = self._get_unit_name(unit_type, unit_data)
            # Create instance of unit and add to relevant group
            unit_group = getattr(self, units.SUPPORTED_UNIT_TYPES[unit_type]["group"])
            self._add_unit_to_group(unit_group, unit_type, unit_name, unit_data)

    def _get_unit_name(self, unit_type, unit_data):
        # Check if the unit type has associated subtypes
        if units.SUPPORTED_UNIT_TYPES[unit_type]["has_subtype"]:
            return unit_data[2][: self._label_len].strip()
        return unit_data[1][: self._label_len].strip()

    def _add_unit_to_group(self, unit_group, unit_type, unit_name, unit_data):
        # Raise exception if a duplicate label is encountered
        if unit_name in unit_group:
            msg = f'Duplicate label ({unit_name}) encountered within category: {units.SUPPORTED_UNIT_TYPES[unit_type]["group"]}'
            raise Exception(msg)
        # Changes done to account for unit types with spaces/dashes eg Flat-V Weir
        unit_type_safe = unit_type.replace(" ", "_").replace("-", "_")
        unit_group[unit_name] = eval(
            f"units.{unit_type_safe}({unit_data}, {self._label_len})",
        )
        self._all_units.append(unit_group[unit_name])

    def _process_unsupported_unit(self, unit_type, unit_data):
        # Check to see whether unit type has associated subtypes so that unit name can be correctly assigned
        unit_name, subtype = self._get_unsupported_unit_name(unit_type, unit_data)
        self._unsupported[f"{unit_name} ({unit_type})"] = units.UNSUPPORTED(
            unit_data,
            self._label_len,
            unit_name=unit_name,
            unit_type=unit_type,
            subtype=subtype,
        )
        self._all_units.append(self._unsupported[f"{unit_name} ({unit_type})"])

    def _get_unsupported_unit_name(self, unit_type, unit_data):
        # Check if the unit type has associated subtypes
        if units.UNSUPPORTED_UNIT_TYPES[unit_type]["has_subtype"]:
            return unit_data[2][: self._label_len].strip(), True
        return unit_data[1][: self._label_len].strip(), False

    def _update_dat_struct(self) -> None:
        """Internal method used to update self._dat_struct which details the overall structure of the dat file as a list of blocks, each of which
        are a dictionary containing the 'start', 'end' and 'type' of the block.
        """
        self._dat_struct = []
        in_block = False
        in_general = True
        in_comment = False
        comment_n: int | None = None  # Used as counter for number of lines in a comment block
        gisinfo_block = False
        general_block = {"start": 0, "Type": "GENERAL"}
        unit_block: dict[str, Any] = {}

        for idx, line in enumerate(self._raw_data):
            # Deal with 'general' header
            if in_general:
                self._process_general_block(line, idx, general_block)
                in_general = False if line == "END GENERAL" else in_general
                continue

            # Deal with comment blocks explicitly as they could contain unit keywords
            if in_comment and comment_n is None:
                comment_n = int(line.strip())
                continue
            if in_comment and comment_n is not None:
                comment_n -= 1
                if comment_n <= 0:
                    unit_block["end"] = idx + comment_n  # add ending index
                    # append existing block to the dat_struct
                    self._dat_struct.append(unit_block)
                    unit_block = {}  # reset block
                    in_comment = False
                    in_block = False
                    comment_n = None
                continue  # move onto next line as still in comment block

            if line == "COMMENT":
                in_comment = True
                unit_block, in_block = self._close_struct_block(
                    "COMMENT",
                    unit_block,
                    in_block,
                    idx,
                )
                continue

            if line == "GISINFO":
                gisinfo_block = True
                unit_block, in_block = self._close_struct_block(
                    "GISINFO",
                    unit_block,
                    in_block,
                    idx,
                )

            if not gisinfo_block:
                unit_type = self._identify_unit_type(line)
                if unit_type:
                    unit_block, in_block = self._close_struct_block(
                        unit_type,
                        unit_block,
                        in_block,
                        idx,
                    )

        self._finalize_last_block(unit_block)

    def _process_general_block(
        self,
        line: str,
        idx: int,
        general_block: dict[str, Any],
    ) -> None:
        # Deal with 'general' header
        if line == "END GENERAL":
            general_block["end"] = idx
            self._dat_struct.append(general_block)

    def _identify_unit_type(self, line: str) -> str | None:
        # Check to see whether unit type has associated subtypes so that unit name can be correctly assigned
        if line.split(" ")[0] in units.ALL_UNIT_TYPES:
            # The " " is needed here in case of empty string
            return line.split()[0]
        if " ".join(line.split()[:2]) in units.ALL_UNIT_TYPES:
            return " ".join(line.split()[:2])
        return None

    def _finalize_last_block(
        self,
        unit_block: dict[str, Any],
    ) -> None:
        if len(unit_block) != 0:
            # Only adds end block if there is a block present (i.e. an empty DAT stays empty)
            # add ending index for final block
            unit_block["end"] = len(self._raw_data) - 1
            self._dat_struct.append(unit_block)  # add final block

    def _close_struct_block(
        self,
        unit_type: str,
        unit_block: dict,
        in_block: bool,
        idx: int,
    ) -> tuple[dict, bool]:
        """Helper method to close block in dat struct"""
        if in_block is True:
            unit_block["end"] = idx - 1  # add ending index
            # append existing bdy block to the dat_struct
            self._dat_struct.append(unit_block)
            unit_block = {}  # reset bdy block
        in_block = True
        unit_block["Type"] = unit_type  # start new bdy block
        unit_block["start"] = idx  # add starting index

        return unit_block, in_block

    @handle_exception(when="remove unit from")
    def remove_unit(self, unit: Unit) -> None:
        """Remove a unit from the dat file.

        Args:
            unit (Unit): flood modeller unit input.

        Raises:
            TypeError: Raised if given unit isn't an instance of FloodModeller Unit.
        """
        # catch if not valid unit
        if not isinstance(unit, Unit):
            msg = "unit isn't a unit"
            raise TypeError(msg)

        # remove from all units
        index = self._all_units.index(unit)
        del self._all_units[index]
        # remove from dat_struct
        dat_struct_unit = self._dat_struct[index + 1]
        del self._dat_struct[index + 1]
        # remove from raw data
        del self._raw_data[dat_struct_unit["start"] : dat_struct_unit["end"] + 1]
        # remove from unit group
        unit_group_name = units.SUPPORTED_UNIT_TYPES[unit._unit]["group"]
        unit_group = getattr(self, unit_group_name)
        del unit_group[unit.name]
        # remove from ICs
        self.initial_conditions.data = self.initial_conditions.data.loc[
            self.initial_conditions.data["label"] != unit.name
        ]

        self._update_dat_struct()
        self.general_parameters["Node Count"] -= 1

    @handle_exception(when="insert unit into")
    def insert_unit(  # noqa: C901, PLR0912
        self,
        unit: Unit,
        add_before: Unit | None = None,
        add_after: Unit | None = None,
        add_at: int | None = None,
        defer_update: bool = False,
    ) -> None:
        """Inserts a unit into the dat file.

        Args:
            unit (Unit): FloodModeller unit input.
            add_before (Unit): FloodModeller unit to add before.
            add_after (Unit): FloodModeller unit to add after.
            add_at (integer): Positional argument (starting at 0) of where to add in
                the dat file. To add at the end of the network you can use -1.

        Raises:
            SyntaxError: Raised if no positional argument is given.
            TypeError: Raised if given unit isn't an instance of FloodModeller Unit.
            NameError: Raised if unit name already appears in unit group.
        """
        # catch errors
        provided_params = sum(arg is not None for arg in (add_before, add_after, add_at))
        if provided_params == 0:
            msg = "No positional argument given. Please provide either add_before, add_at or add_after"
            raise SyntaxError(msg)
        if provided_params > 1:
            msg = "Only one of add_at, add_before, or add_after required"
            raise SyntaxError(msg)
        if not isinstance(unit, Unit):
            msg = "unit isn't a unit"
            raise TypeError(msg)
        if add_at is None and not (isinstance(add_before, Unit) or isinstance(add_after, Unit)):
            msg = "add_before or add_after argument must be a Flood Modeller Unit type"
            raise TypeError(msg)

        unit_class = unit._unit
        if unit_class != "COMMENT":
            _validate_unit(unit)
            unit_group_name = units.SUPPORTED_UNIT_TYPES[unit._unit]["group"]
            unit_group = getattr(self, unit_group_name)
            if unit.name in unit_group:
                msg = "Name already appears in unit group. Cannot have two units with same name in same group"
                raise NameError(msg)

        # positional argument
        if add_at is not None:
            insert_index = add_at
            if insert_index < 0:
                insert_index += len(self._all_units) + 1
                if insert_index < 0:
                    msg = f"invalid add_at index: {add_at}"
                    raise Exception(msg)
        else:
            check_unit = add_before or add_after
            for index, thing in enumerate(self._all_units):
                if thing == check_unit:
                    insert_index = index
                    insert_index += 1 if add_after else 0
                    break
            else:
                msg = (
                    f"{check_unit} not found in dat network, so cannot be used to add before/after"
                )
                raise Exception(msg)

        unit_data = unit._write()
        self._all_units.insert(insert_index, unit)
        if unit._unit != "COMMENT":
            unit_group[unit.name] = unit
        self._dat_struct.insert(
            insert_index + 1,
            {"Type": unit_class, "new_insert": unit_data},
        )  # add to dat struct without unit.name

        if unit._unit != "COMMENT":
            # update the iic's tables
            iic_data = [unit.name, "y", 00.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            self.initial_conditions.data.loc[len(self.initial_conditions.data)] = iic_data  # flaged

        # update all
        if unit._unit != "COMMENT":
            self.general_parameters["Node Count"] += 1  # flag no update for comments

        if not defer_update:
            self._update_raw_data()
            self._update_dat_struct()

    def insert_units(
        self,
        units: list[Unit],
        add_before: Unit | None = None,
        add_after: Unit | None = None,
        add_at: int | None = None,
    ) -> None:
        """Inserts a list of units into the dat file.

        Args:
            units (list[Unit]): List of FloodModeller units.
            add_before (Unit): FloodModeller unit to add before.
            add_after (Unit): FloodModeller unit to add after.
            add_at (integer): Positional argument (starting at 0) of where to add in
                the dat file. To add at the end of the network you can use -1.
        """
        ordered = (add_at is None and add_after is None) or (isinstance(add_at, int) and add_at < 0)
        ordered_units = units if ordered else units[::-1]
        for unit in ordered_units:
            self.insert_unit(unit, add_before, add_after, add_at, defer_update=True)
        self._update_raw_data()
        self._update_dat_struct()

    def _update_gisinfo_label(
        self,
        unit_type,
        unit_subtype,
        prev_lbl,
        new_lbl,
        ignore_second,
    ):
        """Update labels in GISINFO block if unit is renamed"""

        start, end = next(
            (block["start"], block["end"])
            for block in self._dat_struct
            if block["Type"] == "GISINFO"
        )
        gisinfo_block = self._raw_data[start : end + 1]

        prefix = unit_type if unit_subtype is None else f"{unit_type} {unit_subtype}"

        new_gisinfo_block = []
        for line in gisinfo_block:
            # Replace first label
            if line.startswith(f"{prefix} {prev_lbl} "):
                # found matching line (space at the end is important to ignore node
                # lables with similar starting chars)
                line = line.replace(f"{prefix} {prev_lbl} ", f"{prefix} {new_lbl} ")

            # Replace second label
            if not ignore_second and line.startswith(
                f"{prev_lbl} ",
            ):  # space at the end important again
                line = line.replace(f"{prev_lbl} ", f"{new_lbl} ", 1)

            new_gisinfo_block.append(line)

        self._raw_data[start : end + 1] = new_gisinfo_block

    def _update_gxy_label(
        self,
        unit_type: str,
        unit_subtype: str,
        prev_lbl: str,
        new_lbl: str,
    ) -> None:
        """Update labels in GXY file if unit is renamed"""

        if self._gxy_data is not None:
            if unit_subtype is None:
                unit_subtype = ""

            old = f"{unit_type}_{unit_subtype}_{prev_lbl}"
            new = f"{unit_type}_{unit_subtype}_{new_lbl}"

            self._gxy_data = self._gxy_data.replace(old, new)
