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
from floodmodeller_api.units.helpers import (
    split_n_char,
    _to_float,
    _to_str,
    join_n_char_ljust,
)
from floodmodeller_api.validation import _validate_unit

class CONDUIT(UrbanUnit):
    """Class to hold and process CONDUIT unit type

    Args:
        self.name (str): Unit name. (required)
        self.node1 (str): Name of upstream node. (required)
        self.node2 (str): Name of downstream node. (required)
        self.length (float): Conduit length (ft or m). (required)
        self.n (float): Mannings n value. (required)
        self.z1 (float): Offset of upstream end of conduit invert above the invert elevation of it's upstream node (ft or m). (required)
        self.z1 (float): Offset of downstream end of conduit invert above the invert elevation of it's downstream node (ft or m). (required)
        self.q0 (float): Flow in conduit at start of simulation (flow units).(optional, default 0)
        self.qmax (float): maximum flow allowed in the conduit (flow units) (optional, default unlimited)

    Returns:
        CONDUIT: Flood Modeller CONDUIT Unit class object
    """
    _unit = "CONDUIT"

    def _read(self, line):
        """Function to read a given CONDUIT line and store data as class attributes"""
        
        
        # TODO: add functionality to read comments - these are provided in a comment line above data line in the node subsection (comment line  starts with a ;)

        unit_data = line.split()  # Get unit parameters

        # Extend length of unit_data if options varaibales not provided.
        while len(unit_data) < 9:
            unit_data.append("")


        # TODO: Update defaults.  Presently atrbitary defaults added to allow API to work. 
        # TODO: Consider renaming variables.  Currently named as per SWMM manual.  However, more descriptive names are used in Flood Modeller.  E.g. node1 =  inlet node 

        self.name = _to_str(unit_data[0],"") 
        self.node1 = _to_str(unit_data[1],"") 
        self.node2 = _to_str(unit_data[2], "") 
        self.length = _to_float(unit_data[3], 0)
        self.n = _to_float(unit_data[4], 0.0) 
        self.z1 = _to_float(unit_data[5], 0.0) 
        self.z2 = _to_float(unit_data[6], 0.0) 
        self.q0 = _to_float(unit_data[7], 0.0) # Default as per FM
        self.qmax = _to_float(unit_data[8], 999999) # Default as per FM

        # This class reads data classified as [CONDUITS] within the INP file however additional related parameters are also the shape and loss attributes
        # and so the data for this consuit is incomplete

        #TODO: Need to consider adding shape (from [XSECTIONS]) and losses (from [Losses])
        
    def _write(self):
        """Function to write a valid CONDUIT line"""

        _validate_unit(self, urban = True)

        return join_n_char_ljust(15, self.name, self.node1, self.node2, self.length, self.n, self.z1, self.z2, self.q0, self.qmax)

        
class CONDUITS(UrbanSubsection):
    """Class to read/write the table of junctions"""

    _urban_unit_class = CONDUIT
    _attribute = "conduits"

    #TODO: refresh how these internal variables are used


