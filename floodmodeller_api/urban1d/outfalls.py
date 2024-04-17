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


class OUTFALL(UrbanUnit):
    """Class to hold and process OUTFALL unit type

    Args:
        name (str): Unit name
        elevation (float): Elevation of outfall invert (ft or m). (required)
        type (string): "FREE", "NORMAL", "FIXED", "TIDAL" or "TIMESERIES". (required)
        stage (float): elevation of fixed stage for outfall (ft or m) (required when "FIXED" type)
        tcurve (string): name of curve in [CURVES] section containing tidal height (required when "TIDAL" type)
        tseries (string): name of timeseries in [TIMESERIES] section that describes how outfall stage varies with time (required when "TIMESERIES" type)
        gated (sring): "YES" or "NO" depending on whether flat gate is present that prevents reverse flow. (optional for all types, default is "NO") TODO: is this required, or can it be missing
        routeto (string): Optional name of a subcatchment that recieves the outfall's discharge. (default is not be "", and to no route outfall's discharge)

    Returns:
        OUTFALL: Flood Modeller OUTFALL Unit class object TODO: add urban 1d in to all instances within urban 1d API
    """

    _unit = "OUTFALL"
    MIN_LENGTH_FREE_NORMAL = 5
    MIN_LENGTH_FIXED_NORMAL_TIMESERIES = 6

    def _read(self, line):
        unit_data = line.split()

        # TODO: add functionality to read comments
        # TODO: considering raising an exception if any of the required parameters are missing

        self.name = str(unit_data[0])
        self.elevation = _to_float(unit_data[1], 0.0)
        self.type = str(unit_data[2])

        if self.type in ("FREE", "NORMAL"):
            # Extend length of unit_data to account for missing optional arguments.
            while len(unit_data) < self.MIN_LENGTH_FREE_NORMAL:
                unit_data.append("")

            self.gated = _to_str(unit_data[3], "NO")
            self.routeto = _to_str(unit_data[4], "")

        elif self.type in ("FIXED", "NORMAL", "TIMESERIES"):
            # Extend length of unit_data to account for missing optional arguments.
            while len(unit_data) < self.MIN_LENGTH_FIXED_NORMAL_TIMESERIES:
                unit_data.append("")

            if self.type == "FIXED":
                self.stage = _to_float(unit_data[3], 0.0)

            elif self.type == "NORMAL":
                self.tcurve = _to_str(unit_data[3], "")

            elif self.type == "TIMESERIES":
                self.tseries = _to_str(unit_data[3], "")

            self.gated = _to_str(unit_data[4], "NO")
            self.routeto = _to_str(unit_data[5], "")

    def _write(self):
        """Function to write a valid OUTFALL line"""

        _validate_unit(self, urban=True)

        # TODO:Improve indentation format when writing and include header for completeness

        params1 = join_n_char_ljust(17, self.name) + join_n_char_ljust(
            15,
            self.elevation,
            self.type,
        )

        if self.type in ("FREE", "NORMAL"):
            params2 = join_n_char_ljust(15, "", self.gated, self.routeto)

        elif self.type == "FIXED":
            params2 = join_n_char_ljust(15, self.stage, self.gated, self.routeto)

        elif self.type == "NORMAL":
            params2 = join_n_char_ljust(15, self.tcurve, self.gated, self.routeto)

        elif self.type == "TIMESERIES":
            params2 = join_n_char_ljust(15, self.tseries, self.gated, self.routeto)

        else:
            raise RuntimeError(f"{self.type} not supported")

        return params1 + params2


class OUTFALLS(UrbanSubsection):
    """Class to read/write the table of outfalls"""

    _urban_unit_class = OUTFALL
    _attribute = "outfalls"
