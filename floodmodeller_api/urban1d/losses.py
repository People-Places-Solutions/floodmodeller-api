"""
Flood Modeller Python API
Copyright (C) 2024 Jacobs U.K. Limited

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see https://www.gnu.org/licenses/.

If you have any query about this program or this License, please contact us at support@floodmodeller.com or write to the following
address: Jacobs UK Limited, Flood Modeller, Cottons Centre, Cottons Lane, London, SE1 2QG, United Kingdom.
"""

from floodmodeller_api.units.helpers import _to_float, _to_str, join_n_char_ljust
from floodmodeller_api.validation import _validate_unit

from ._base import UrbanSubsection, UrbanUnit


class LOSS(UrbanUnit):
    """Class to hold and process LOSS unit type

    Args:
        name (str): Name of conduit. (required)
        kentry (float): Entrance minor head loss coefficient. (required) # TODO: FM name - Entry Loss Coeff.
        kexit (float): Exit minor head loss coefficient. (required) # TODO: FM name - Exit Loss Coeff.
        kavg (float): Average minor head loss coefficient across lenght of culvert. (required) # TODO: FM name - Avg. Loss Coeff.
        flap (str): YES/NO.  If conduit has a flat valve that prevents back flow. (optional, default NO ) # TODO: FM name - Flap Gate.
        seepage (float): Rate of seepage loss into surrounding soil (in/hr or mm/hr). (optional, default is 0) # TODO: FM name - Seepage Loss Rate


    Returns:
        LOSS: Flood Modeller LOSS Unit class object
    """

    _unit = "LOSS"
    MIN_LENGTH = 6

    def _read(self, line):
        """Function to read a given LOSS line and store data as class attributes"""

        # TODO: add functionality to read comments

        unit_data = line.split()  # Get unit parameters

        # Extend length of unit_data if options variables not provided.
        while len(unit_data) < self.MIN_LENGTH:
            unit_data.append("")

        self.name = _to_str(unit_data[0], "")
        self.kentry = _to_float(unit_data[1], 0)
        self.kexit = _to_float(unit_data[2], 0)
        self.kavg = _to_float(unit_data[3], 0)
        self.flap = _to_str(unit_data[4], "NO")
        self.seepage = _to_float(unit_data[5], 0)

    def _write(self):
        """Function to write a valid LOSS line"""

        _validate_unit(self, urban=True)

        # TODO:Improve indentation format when writing and include header for completeness

        return join_n_char_ljust(17, self.name) + join_n_char_ljust(
            15,
            self.kentry,
            self.kexit,
            self.kavg,
            self.flap,
            self.seepage,
        )


class LOSSES(UrbanSubsection):
    """Class to read/write the table of losses"""

    _urban_unit_class = LOSS
    _attribute = "losses"
