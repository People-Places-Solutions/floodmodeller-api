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

from floodmodeller_api.units._helpers import join_n_char_ljust, to_float, to_int
from floodmodeller_api.validation import _validate_unit

from ._base import UrbanSubsection, UrbanUnit


class XSECTION(UrbanUnit):
    """Class to hold and process XSECTION unit type

    Args:
        name (str): Link name of the conduit, orifice, or weir. (required)
        shape (str): cross-section shape type (see Tables D-1  or 3-1 for available shapes). (required)
        geom1 (float): Full height of the cross-section (ft or m). (required, for shape types or "CUSTOM" or "IREGULAR)
        geom2 (float): auxiliary parameter (width, side slopes, etc.) as listed in Table D-1. (required, applicable to shape types)
        geom3 (float): auxiliary parameter (width, side slopes, etc.) as listed in Table D-1. (required, applicable to shape types)
        geom4 (float):auxiliary parameter (width, side slopes, etc.) as listed in Table D-1. (required, applicable to shape types)
        barrels (float): Barrels type  number of barrels (i.e., number of parallel pipes of equal size, slope, and roughness) associated with a conduit of shape type , or "CUSTOM" type (optional, default is 1).
        culvert (int): Culvert code number from Table A.10 for the conduit's inlet geometry if it is a culvert subject to possible inlet flow control.  Only an option for shape type (leave blank otherwise) (optional, default is "").
        curve (str): Curve name of a Shape Curve in the [CURVES] section that defines how width varies with depth. (optional, applicable to shape types only)
        tsect (str): Name of an entry in the [TRANSECTS] section that describes the cross-section geometry of an irregular channel. (required, applicable to "IREGUALAR types only)


    Returns:
        XSECTION: Flood Modeller XSECTION Unit class object
    """

    _unit = "XSECTION"
    MIN_LENGTH_OTHER = 8
    MIN_LENGTH_CUSTOM = 5
    MIN_LENGTH_IRREGULAR = 3

    def _read(self, line):
        unit_data = line.split()

        self.name = str(unit_data[0])

        if unit_data[1] in _shape_options:
            # Extend length of unit_data to account for missing optional arguments.

            while len(unit_data) < self.MIN_LENGTH_OTHER:
                unit_data.append("")

            self.shape = str(unit_data[1])
            self.geom1 = to_float(unit_data[2], 0.0)
            self.geom2 = to_float(unit_data[3], 0.0)
            self.geom3 = to_float(unit_data[4], 0.0)
            self.geom4 = to_float(unit_data[5], 0.0)
            self.barrels = to_int(unit_data[6], 1)
            self.culvert = to_int(unit_data[7], "")

        elif unit_data[1] == "CUSTOM":
            while len(unit_data) < self.MIN_LENGTH_CUSTOM:
                unit_data.append("")

            self.shape = str(unit_data[1])
            self.geom1 = to_float(unit_data[2], "")
            self.barrels = to_int(unit_data[6], 1)

        elif unit_data[1] == "IRREGULAR":
            while len(unit_data) < self.MIN_LENGTH_IRREGULAR:
                unit_data.append("")

            self.shape = str(unit_data[1])
            self.tsect = str(unit_data[2])

    def _write(self):
        """Function to write a valid OUTFALL line"""

        _validate_unit(self, urban=True)

        params1 = join_n_char_ljust(17, self.name)

        if self.shape in _shape_options:
            params2 = join_n_char_ljust(
                15,
                self.shape,
                self.geom1,
                self.geom2,
                self.geom3,
                self.geom4,
                self.barrels,
                self.culvert,
            )

        elif self.shape == "CUSTOM":
            params2 = join_n_char_ljust(15, self.shape, self.geom1, self.barrels)

        elif self.shape == "IRREGULAR":
            params2 = join_n_char_ljust(15, self.shape, self.tsect)

        else:
            msg = f"{self.shape} not supported"
            raise RuntimeError(msg)

        return params1 + params2


class XSECTIONS(UrbanSubsection):
    """Class to read/write the table of junctions"""

    _urban_unit_class = XSECTION
    _attribute = "xsections"


_shape_options = [
    "CIRCULAR",
    "FORCE_MAIN",
    "FILLED_CIRCULAR2",
    "RECT_CLOSED",
    "RECT_OPEN",
    "TRAPEZOIDAL",
    "TRIANGULAR",
    "HORIZ_ELLIPSE",
    "VERT_ELLIPSE",
    "ARCH",
    "PARABOLIC",
    "POWER",
    "RECT_TRIANGULAR",
    "RECT_ROUND",
    "MODBASKETHANDLE",
    "EGG",
    "HORSESHOE",
    "GOTHIC",
    "CATENARY",
    "SEMIELLIPTICAL",
    "BASKETHANDLE",
    "SEMICIRCULAR",
]
