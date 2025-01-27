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


class RAINGAUGE(UrbanUnit):
    """Class to hold and process RAINGAUGE unit type

    Args:
        name (str): Unit name
        format (str): Form of recorded rainfall, either 'INTENSITY', 'VOLUME' or 'CUMULATIVE' (mandatory)
        interval (float): Time interval between gauge readings in decimal hours or hours:minutes format (e.g., 0:15 for 15-minute readings). (mandatory)
        snow_catch_factor (float): Snow catch deficiency correction factor (SCF) (use 1.0 for no adjustment). (mandatory)
        data_option (str):'TIMESERIES' or 'FILE' defining where the data is provdied.
        timeseries (str): Name of time series in [TIMESERIES] section with rainfall data (mandatory, if data_option = 'TIMESERIES')
        filename (str): Name of external file with rainfall data. (mandatory, if data_option = 'File')
        station (str)Name of recording station used in the rain file (mandatory, if data_option = 'File')
        units (str): Rain depth units used in the rain file, either 'IN' (inches) or 'MM' (millimeters).(mandatory, if data_option = 'File')

    Returns:
        RAINGAUGE: Flood Modeller RAINGAUGE Unit class object
    """

    _unit = "RAINGAUGE"

    def _read(self, line):
        """Function to read a given RAINGAUGE line and store data as class attributes"""

        unit_data = line.split()  # Get unit parameters

        self.name = str(unit_data[0])
        self.format = str(unit_data[1])

        try:
            self.interval = float(unit_data[2])  # Decimal hours
        except ValueError:
            self.interval = str(unit_data[2])  # HH:MM format

        self.snow_catch_factor = to_float(unit_data[3], 0.0)
        self.data_option = str(unit_data[4])

        # Check is raingauge data is provided as a TIMESERIES or as a FILE
        if self.data_option == "TIMESERIES":
            self.timeseries = str(unit_data[5])

            # Creates empty fields to allow user to change data_option
            self.filename = ""
            self.station = ""
            self.units = "MM"
        elif self.data_option == "FILE":
            self.filename = str(unit_data[5])
            self.station = str(unit_data[6])
            self.units = str(unit_data[7])

            # Creates empty fields to allow user to change data_option
            self.timeseries = ""

    def _write(self):
        """Function to write a valid JUNCTION line"""

        _validate_unit(self, urban=True)

        params1 = join_n_char_ljust(17, self.name) + join_n_char_ljust(
            15,
            self.format,
            self.interval,
            self.snow_catch_factor,
            self.data_option,
        )  # First group of parameters

        # Second group of parameters
        if self.data_option == "TIMESERIES":
            params2 = self.timeseries

        elif self.data_option == "FILE":
            params2 = join_n_char_ljust(15, self.filename, self.station, self.units)

        else:
            msg = f"{self.data_option} not supported"
            raise RuntimeError(msg)

        return params1 + params2


class RAINGAUGES(UrbanSubsection):
    """Class to read/write the table of raingauges"""

    _urban_unit_class = RAINGAUGE
    _attribute = "raingauges"
