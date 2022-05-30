from ._base import UrbanSubsection, UrbanUnit
from floodmodeller_api.units.helpers import (
    split_n_char,
    _to_float,
    _to_str,
    join_n_char_ljust,
)
from floodmodeller_api.validation import _validate_unit


class JUNCTION(UrbanUnit):
    """Class to hold and process JUNCTION unit type

    Args:
        self.name (str): Unit name
        self.elevation (float): Elevation of junction invert (ft or m). (required)
        self.max_depth (float): Depth from ground to invert elevation (ft or m) (default is 0). (optional)
        self.initial_depth (float): Water depth at start of simulation (ft or m) (default is 0). (optional)
        self.surface_depth (float): Maximum additional head above ground elevation that manhole junction can sustain under surcharge conditions (ft or m) (default is 0). (optional)
        self.area_ponded (float): Area subjected to surface ponding once water depth exceeds Ymax (ft2 or m2) (default is 0) (optional).

    Returns:
        JUNCTION: Flood Modeller JUNCTION Unit class object
    """

    _unit = "JUNCTION"

    def _read(self, line):
        """Function to read a given JUNCTION line and store data as class attributes"""

        # TODO: add functionality to read comments - these are provided in a comment line above data line in the node subsection (comment line  starts with a ;)

        unit_data = line.split()  # Get unit parameters

        while (
            len(unit_data) < 6
        ):  # Extend length of unit_data if options varaibales not provided.
            unit_data.append("")

        self.name = str(unit_data[0])

        self.elevation = _to_float(unit_data[1], 0.0)
        self.max_depth = _to_float(unit_data[2], 0.0)
        self.initial_depth = _to_float(unit_data[3], 0.0)
        self.surface_depth = _to_float(unit_data[4], 0.0)
        self.area_ponded = _to_float(unit_data[5], 0.0)

    def _write(self):
        """Function to write a valid JUNCTION line"""

        _validate_unit(self, urban=True)

        # TODO:Improve indentation format when writing.  Consider writing header rows for clarity and completness

        return join_n_char_ljust(
            15,
            self.name,
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
