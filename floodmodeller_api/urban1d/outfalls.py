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

from ._base import UrbanSubsection, UrbanUnit

# from floodmodeller_api.units.helpers import split_n_char, _to_float, _to_str


from ._base import UrbanSubsection, UrbanUnit
from floodmodeller_api.units.helpers import (
    split_n_char,
    _to_float,
    _to_str,
    join_n_char_ljust,
)
from floodmodeller_api.validation import _validate_unit


# class OUTFALL(UrbanUnit): #TODO: need to update to be 'JUNCTION' with no S
#     """ TO BE COMPLETED
#     """

#     _unit = 'OUTFALL' # NOTE: this is used to assigned class name via setter

#     def _read(self, line):

#         unit_data = line.split()

#         while len(unit_data)<6:
#             unit_data.append('')

#         self.name = str(unit_data[0]) #TODO: update once Class inheritance sorted.
#         #TODO: need to catch instence when optional parameters are not provided
#         self.elevation = _to_float(unit_data[1], 0.0) # Elevation of junction invert (ft or m). (required)
#         self.type = str(unit_data[2]) # Depth from ground to invert elevation (ft or m) (default is 0). (optional)
#         self.stage_data = _to_float(unit_data[3], 0.0) # Water depth at start of simulation (ft or m) (default is 0). (optional)
#         self.gated = str(unit_data[4]) # Maximum additional head above ground elevation that manhole junction can sustain under surcharge conditions (ft or m) (default is 0). (optional)
#         self.route_to = _to_float(unit_data[5], 0.0) # Area subjected to surface ponding once water depth exceeds Ymax (ft2 or m2) (default is 0) (optional).

#     def _write(self):

#         #TODO:Improve indentation
#         return join_n_char_ljust(15, self.name, self.elevation, self.max_depth, self.initial_depth, self.surface_depth, self.area_ponded)

# class OUTFALLS(UrbanSubsection):
#     ''' Class to read the table of junctions'''
#     _urban_unit_class = OUTFALL
#     _attribute = 'outfalls'
