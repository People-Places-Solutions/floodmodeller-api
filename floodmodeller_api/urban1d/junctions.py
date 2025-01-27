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

from floodmodeller_api.units._helpers import join_n_char_ljust, to_float
from floodmodeller_api.validation import _validate_unit

from ._base import UrbanSubsection, UrbanUnit


class JUNCTION(UrbanUnit):
    """Class to hold and process JUNCTION unit type

    Args:
        name (str): Unit name
        elevation (float): Elevation of junction invert (ft or m). (required)
        max_depth (float): Depth from ground to invert elevation (ft or m) (default is 0). (optional)
        initial_depth (float): Water depth at start of simulation (ft or m) (default is 0). (optional)
        surface_depth (float): Maximum additional head above ground elevation that manhole junction can sustain under surcharge conditions (ft or m) (default is 0). (optional)
        area_ponded (float): Area subjected to surface ponding once water depth exceeds Ymax (ft2 or m2) (default is 0) (optional).

    Returns:
        JUNCTION: Flood Modeller JUNCTION Unit class object
    """

    _unit = "JUNCTION"
    MIN_LENGTH = 6

    def _read(self, line):
        """Function to read a given JUNCTION line and store data as class attributes"""

        unit_data = line.split()  # Get unit parameters

        # Extend length of unit_data if options variables not provided.
        while len(unit_data) < self.MIN_LENGTH:
            unit_data.append("")

        self.name = str(unit_data[0])

        self.elevation = to_float(unit_data[1], 0.0)
        self.max_depth = to_float(unit_data[2], 0.0)
        self.initial_depth = to_float(unit_data[3], 0.0)
        self.surface_depth = to_float(unit_data[4], 0.0)
        self.area_ponded = to_float(unit_data[5], 0.0)

    def _write(self):
        """Function to write a valid JUNCTION line"""

        _validate_unit(self, urban=True)

        return join_n_char_ljust(17, self.name) + join_n_char_ljust(
            15,
            self.elevation,
            self.max_depth,
            self.initial_depth,
            self.surface_depth,
            self.area_ponded,
        )


class JUNCTIONS(UrbanSubsection):
    """Class to read/write the table of junctions"""

    _urban_unit_class = JUNCTION
    _attribute = "junctions"
