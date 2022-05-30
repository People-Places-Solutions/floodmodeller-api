from ._base import UrbanSubsection, UrbanUnit
from floodmodeller_api.units.helpers import (
    split_n_char,
    _to_float,
    _to_str,
    join_n_char_ljust,
)
from floodmodeller_api.validation import _validate_unit


class RAINGAUGE(UrbanUnit):
    """Class to hold and process RAINGAUGE unit type

    Args:
        self.name (str): Unit name
        self.format (str): Form of recorded rainfall, either 'INTENSITY', 'VOLUME' or 'CUMULATIVE' (mandatory)
        self.interval (float): Time interval between gauge readings in decimal hours or hours:minutes format (e.g., 0:15 for 15-minute readings). (mandatory)
        self.snow_catch_factor (float): Snow catch deficiency correction factor (SCF) (use 1.0 for no adjustment). (mandatory)
        self.data_option (str):'TIMESERIES' or 'FILE' defining where the data is provdied.
        self.timeseries (str): Name of time series in [TIMESERIES] section with rainfall data (mandatory, if data_option = 'TIMESERIES')
        self.filename (str): Name of external file with rainfall data. (mandatory, if data_option = 'File')
        self.station (str)Name of recording station used in the rain file (mandatory, if data_option = 'File')
        self.units (str): Rain depth units used in the rain file, either 'IN' (inches) or 'MM' (millimeters).(mandatory, if data_option = 'File')

    Returns:
        RAINGAUGE: Flood Modeller RAINGAUGE Unit class object
    """

    _unit = "RAINGAUGE"

    def _read(self, line):
        """Function to read a given RAINGAUGE line and store data as class attributes"""

        # TODO: add functionality to read comments - these are provided in a comment line above data line in the node subsection (comment line  starts with a ;)

        unit_data = line.split()  # Get unit parameters

        self.name = str(unit_data[0])
        self.format = str(unit_data[1])

        try:
            self.interval = float(unit_data[2])  # Decimal hours
        except ValueError:
            self.interval = str(unit_data[2])  # HH:MM format

        self.snow_catch_factor = _to_float(unit_data[3], 0.0)
        self.data_option = str(unit_data[4])

        # Check is raingauge data is provided as a TIMESERIES or as a FILE
        if self.data_option == "TIMESERIES":
            self.timeseries = str(unit_data[5])

            # Creates empty fields to allow user to change data_option
            self.filename = str("")
            self.station = str("")
            self.units = "MM"
        elif self.data_option == "FILE":
            self.filename = str(unit_data[5])
            self.station = str(unit_data[6])
            self.units = str(unit_data[7])

            # Creates empty fields to allow user to change data_option
            self.timeseries = str("")

    def _write(self):
        """Function to write a valid JUNCTION line"""

        _validate_unit(self, urban=True)

        # TODO:Improve indentation format when writing.  Consider writing header rows for clarity and completness

        params1 = join_n_char_ljust(
            15,
            self.name,
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

        return params1 + params2

        # TODO: Implement validation that does not allow any spaces to be entered in attribute values


class RAINGAUGES(UrbanSubsection):
    """Class to read/write the table of raingauges"""

    _urban_unit_class = RAINGAUGE
    _attribute = "raingauges"
