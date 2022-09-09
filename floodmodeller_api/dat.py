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

from pathlib import Path
from typing import Optional, Union

from . import units  # Import for using as package
from ._base import FMFile
from floodmodeller_api.units.helpers import _to_str, _to_float, _to_int, _to_data_list


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

    def __init__(self, dat_filepath: Optional[Union[str, Path]] = None):
        try:
            self._filepath = dat_filepath
            if self._filepath != None:
                FMFile.__init__(self)
                self._read()

            else:
                self._create_from_blank()

            self._get_general_parameters()
            self._get_unit_definitions()
        except Exception as e:
            self._handle_exception(e, when="read")

    def update(self) -> None:
        """Updates the existing DAT based on any altered attributes"""
        self._update()

    def save(self, filepath: Union[str, Path]) -> None:
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
        if not self._gxy_data == None:
            gxy_string = self._gxy_data
            new_gxy_path = filepath.with_suffix(".gxy")
            with open(new_gxy_path, "w") as gxy_file:
                gxy_file.write(gxy_string)
            self._gxy_filepath = new_gxy_path

    def diff(self, other: "DAT", force_print: bool = False) -> None:
        """Compares the DAT class against another DAT class to check whether they are
        equivalent, or if not, what the differences are. Two instances of a DAT class are
        deemed equivalent if all of their attributes are equal except for the filepath and
        raw data. For example, two DAT files from different filepaths that had the same
        data except maybe some differences in decimal places and some default parameters
        ommitted, would be classed as equaivalent as they would produce the same DAT instance
        and write the exact same data.

        The result is printed to the console. If you need to access the returned data, use
        the method ``DAT._get_diff()``

        Args:
            other (floodmodeller_api.DAT): Other instance of a DAT class
            force_print (bool): Forces the API to print every difference found, rather than
                just the first 25 differences. Defaults to False.
        """
        self._diff(other, force_print=force_print)

    def _read(self):
        # Read DAT data
        with open(self._filepath, "r") as dat_file:
            self._raw_data = [line.rstrip("\n") for line in dat_file.readlines()]

        # Generate DAT structure
        self._update_dat_struct()

        # Get network .gxy if present
        gxy_path = self._filepath.with_suffix(".gxy")
        if gxy_path.exists():
            self._gxy_filepath = gxy_path
            with open(self._gxy_filepath, "r") as gxy_file:
                self._gxy_data = gxy_file.read()
        else:
            self._gxy_filepath = None
            self._gxy_data = None

    def _write(self) -> str:
        """Returns string representation of the current DAT data

        Returns:
            str: Full string representation of DAT in its most recent state (including changes not yet saved to disk)
        """
        try:
            self._update_raw_data()
            self._update_general_parameters()
            self._update_dat_struct()
            self._update_unit_names()

            dat_string = ""
            for line in self._raw_data:
                dat_string += line + "\n"

            return dat_string

        except Exception as e:
            self._handle_exception(e, when="write")

    def _create_from_blank(self):
        # No filepath specified, create new 'blank' DAT in memory
        # ** Update these to have minimal data needed (general header, empty IC header)
        self._dat_struct = [
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

    def _get_general_parameters(self):
        # ** Get general parameters here
        self.title = self._raw_data[0]
        self.general_parameters = {}
        params = units.helpers.split_10_char(self._raw_data[2])
        if len(params) == 6:
            # Adds the measurements unit if not specified
            params.append("DEFAULT")
        params.extend(units.helpers.split_10_char(self._raw_data[3]))

        self.general_parameters["Node Count"] = int(params[0])
        self.general_parameters["Lower Froude"] = _to_float(params[1], 0.75)
        self.general_parameters["Upper Froude"] = _to_float(params[2], 0.9)
        self.general_parameters["Min Depth"] = _to_float(params[3], 0.1)
        self.general_parameters["Convergence Direct"] = _to_float(params[4], 0.001)
        self._label_len = int(params[5])  # label length
        self.general_parameters["Units"] = params[6]  # "DEFAULT" set during read above.
        self.general_parameters["Water Temperature"] = _to_float(params[7], 10)
        self.general_parameters["Convergence Flow"] = _to_float(params[8], 0.1)
        self.general_parameters["Convergence Head"] = _to_float(params[9], 0.1)
        self.general_parameters["Mathematical Damping"] = _to_float(params[10], 0.7)
        self.general_parameters["Pivotal Choice"] = _to_float(params[11], 0.1)
        self.general_parameters["Under-relaxation"] = _to_float(params[12], 0.7)
        self.general_parameters["Matrix Dummy"] = _to_float(params[13], 0)
        self.general_parameters["RAD File"] = self._raw_data[5]  # No default, optional

    def _update_general_parameters(self):
        self._raw_data[0] = self.title
        self._raw_data[5] = self.general_parameters["RAD File"]
        general_params_1 = units.helpers.join_10_char(
            self.general_parameters["Node Count"],
            self.general_parameters["Lower Froude"],
            self.general_parameters["Upper Froude"],
            self.general_parameters["Min Depth"],
            self.general_parameters["Convergence Direct"],
            self._label_len,
        )
        general_params_1 += self.general_parameters["Units"]
        self._raw_data[2] = general_params_1

        general_params_2 = units.helpers.join_10_char(
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
                        raise Exception(
                            f'Error: Cannot update label "{name}" to "{unit.name}" because "{unit.name}" already exists in the Network {unit_group_name} group'
                        )
                    unit_group[unit.name] = unit
                    del unit_group[name]
                    # Update label in ICs
                    if unit_group_name not in ["boundaries", "losses"]:
                        # TODO: Need to do a more thorough check for whether a unit is one in the ICs
                        # e.g. Culvert inlet and river section may have same label, but only river
                        # section label should update in ICs
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
                unit_data = self._raw_data[
                    block["start"] + block_shift : block["end"] + 1 + block_shift
                ]
                prev_block_len = len(unit_data)

                if block["Type"] == "INITIAL CONDITIONS":
                    new_unit_data = self.initial_conditions._write()

                else:
                    if units.SUPPORTED_UNIT_TYPES[block["Type"]]["has_subtype"]:
                        unit_name = unit_data[2][: self._label_len].strip()
                    else:
                        unit_name = unit_data[1][: self._label_len].strip()

                    # Get unit object
                    unit_group = getattr(
                        self, units.SUPPORTED_UNIT_TYPES[block["Type"]]["group"]
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

    def _get_unit_definitions(self):
        # Get unit definitions
        self.sections = {}
        self.boundaries = {}
        self.structures = {}
        self.conduits = {}
        self.losses = {}
        for block in self._dat_struct:
            # Check for all supported boundary types
            if block["Type"] in units.SUPPORTED_UNIT_TYPES:
                unit_data = self._raw_data[block["start"] : block["end"] + 1]

                # Deal with initial conditions block
                if block["Type"] == "INITIAL CONDITIONS":
                    self.initial_conditions = units.IIC(unit_data, n=self._label_len)
                    continue

                # Check to see whether unit type has associated subtypes so that unit name can be correctly assigned
                if units.SUPPORTED_UNIT_TYPES[block["Type"]]["has_subtype"]:
                    unit_name = unit_data[2][: self._label_len].strip()
                else:
                    unit_name = unit_data[1][: self._label_len].strip()

                # Create instance of unit and add to relevant group
                unit_group = getattr(
                    self, units.SUPPORTED_UNIT_TYPES[block["Type"]]["group"]
                )
                if unit_name in unit_group:
                    raise Exception(
                        f'Duplicate label ({unit_name}) encountered within category: {units.SUPPORTED_UNIT_TYPES[block["Type"]]["group"]}'
                    )
                else:
                    #Changes done to account for unit types with spaces/dashes eg Flat-V Weir
                    unit_type = block["Type"].replace(" ","_").replace("-","_")
                    unit_group[unit_name] = eval(
                        f'units.{unit_type}({unit_data}, {self._label_len})'
                    )

    def _update_dat_struct(self):
        """Internal method used to update self._dat_struct which details the overall structure of the dat file as a list of blocks, each of which
        are a dictionary containing the 'start', 'end' and 'type' of the block.

        """
        # Generate DAT structure
        dat_struct = []
        in_block = False
        in_general = True
        in_comment = False
        comment_n = None  # Used as counter for number of lines in a comment block
        gisinfo_block = False
        general_block = {"start": 0, "Type": "GENERAL"}
        unit_block = {}
        for idx, line in enumerate(self._raw_data):
            # Deal with 'general' header
            if in_general == True:
                if line == "END GENERAL":
                    general_block["end"] = idx
                    dat_struct.append(general_block)
                    in_general = False
                    continue
                else:
                    continue

            # Deal with comment blocks explicitly as they could contain unit keywords
            if in_comment and comment_n is None:
                comment_n = int(line.strip())
                continue
            elif in_comment:
                comment_n -= 1
                if comment_n == 0:
                    unit_block["end"] = idx  # add ending index
                    # append existing bdy block to the dat_struct
                    dat_struct.append(unit_block)
                    unit_block = {}  # reset bdy block
                    in_comment = False
                    in_block = False
                    comment_n = None
                    continue
                else:
                    continue  # move onto next line as still in comment block

            if line == "COMMENT":
                in_comment = True
                unit_block, in_block = self._close_struct_block(
                    dat_struct, "COMMENT", unit_block, in_block, idx
                )
                continue

            if line == "GISINFO":
                gisinfo_block = True
                unit_block, in_block = self._close_struct_block(
                    dat_struct, "GISINFO", unit_block, in_block, idx
                )

            if not gisinfo_block:
                if line.split(" ")[0] in units.ALL_UNIT_TYPES:
                    # The " " is needed here in case of empty string
                    unit_type = line.split()[0]
                elif " ".join(line.split()[:2]) in units.ALL_UNIT_TYPES:
                    unit_type = " ".join(line.split()[:2])
                else:
                    continue

                unit_block, in_block = self._close_struct_block(
                    dat_struct, unit_type, unit_block, in_block, idx
                )

        if len(unit_block) != 0:
            # Only adds end block if there is a block present (i.e. an empty DAT stays empty)
            # add ending index for final block
            unit_block["end"] = len(self._raw_data) - 1
            dat_struct.append(unit_block)  # add final block

        self._dat_struct = dat_struct

    def _close_struct_block(self, dat_struct, unit_type, unit_block, in_block, idx):
        """Helper method to close block in dat struct"""
        if in_block == True:
            unit_block["end"] = idx - 1  # add ending index
            # append existing bdy block to the dat_struct
            dat_struct.append(unit_block)
            unit_block = {}  # reset bdy block
        in_block = True
        unit_block["Type"] = unit_type  # start new bdy block
        unit_block["start"] = idx  # add starting index

        return unit_block, in_block

    def insert_unit(unit, prev_block):
        """Placeholder function for adding in new units to DAT"""
        # Get block start/end of prev_block

        # Insert new unit directly into _raw_data

        # Add unit into relevant list (sections, structures, boundaries)

        # Update _dat_struct

        pass

    def _update_gisinfo_label(
        self, unit_type, unit_subtype, prev_lbl, new_lbl, ignore_second
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
            if not ignore_second:
                if line.startswith(f"{prev_lbl} "):  # space at the end important again
                    line = line.replace(f"{prev_lbl} ", f"{new_lbl} ", 1)

            new_gisinfo_block.append(line)

        self._raw_data[start : end + 1] = new_gisinfo_block

    def _update_gxy_label(self, unit_type, unit_subtype, prev_lbl, new_lbl):
        """Update labels in GXY file if unit is renamed"""

        if self._gxy_data is not None:
            if unit_subtype is None:
                unit_subtype = ""

            old = f"{unit_type}_{unit_subtype}_{prev_lbl}"
            new = f"{unit_type}_{unit_subtype}_{new_lbl}"

            self._gxy_data = self._gxy_data.replace(old, new)
