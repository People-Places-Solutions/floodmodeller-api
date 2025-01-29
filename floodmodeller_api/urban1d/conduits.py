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

from floodmodeller_api.units._helpers import join_n_char_ljust, to_float, to_str
from floodmodeller_api.validation import _validate_unit

from ._base import UrbanSubsection, UrbanUnit


class CONDUIT(UrbanUnit):
    """Class to hold and process CONDUIT unit type

    Args:
        name (str): Unit name. (required)
        node1 (str): Name of upstream node. (required)
        node2 (str): Name of downstream node. (required)
        length (float): Conduit length (ft or m). (required)
        n (float): Mannings n value. (required)
        z1 (float): Offset of upstream end of conduit invert above the invert elevation of it's upstream node (ft or m). (required)
        z1 (float): Offset of downstream end of conduit invert above the invert elevation of it's downstream node (ft or m). (required)
        q0 (float): Flow in conduit at start of simulation (flow units).(optional, default 0)
        qmax (float): maximum flow allowed in the conduit (flow units) (optional, default unlimited)

    Returns:
        CONDUIT: Flood Modeller CONDUIT Unit class object
    """

    _unit = "CONDUIT"
    MIN_LENGTH = 9

    def _read(self, line):
        """Function to read a given CONDUIT line and store data as class attributes"""

        unit_data = line.split()  # Get unit parameters

        # Extend length of unit_data if options variables not provided.
        while len(unit_data) < self.MIN_LENGTH:
            unit_data.append("")

        self.name = to_str(unit_data[0], "")
        self.node1 = to_str(unit_data[1], "")
        self.node2 = to_str(unit_data[2], "")
        self.length = to_float(unit_data[3], 0.0)
        self.n = to_float(unit_data[4], 0.0)
        self.z1 = to_float(unit_data[5], 0.0)
        self.z2 = to_float(unit_data[6], 0.0)
        self.q0 = to_float(unit_data[7], 0.0)  # Default as per FM
        self.qmax = to_float(unit_data[8], 999999)  # No limit

    def _write(self):
        """Function to write a valid CONDUIT line"""

        _validate_unit(self, urban=True)

        return join_n_char_ljust(17, self.name, self.node1, self.node2) + join_n_char_ljust(
            15,
            self.length,
            self.n,
            self.z1,
            self.z2,
            self.q0,
            self.qmax,
        )


class CONDUITS(UrbanSubsection):
    """Class to read/write the table of conduits"""

    _urban_unit_class = CONDUIT
    _attribute = "conduits"
