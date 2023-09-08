"""
Flood Modeller Python API
Copyright (C) 2023 Jacobs U.K. Limited

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty 
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details. 

You should have received a copy of the GNU General Public License along with this program.  If not, see https://www.gnu.org/licenses/.

If you have any query about this program or this License, please contact us at support@floodmodeller.com or write to the following 
address: Jacobs UK Limited, Flood Modeller, Cottons Centre, Cottons Lane, London, SE1 2QG, United Kingdom.
"""


import pandas as pd

from ._base import Unit
from .helpers import (
    join_10_char,
    join_12_char_ljust,
    join_n_char_ljust,
    split_10_char,
    split_12_char,
    split_n_char,
    _to_float,
    _to_str,
    _to_int,
    _to_data_list,
)
from floodmodeller_api.validation import _validate_unit


class CONDUIT(Unit):
    """The Conduit class supports two conduit sub-types in Flood Modeller: RECTANGULAR and CIRCULAR. Each of these sub-types forms
    a unique instance of the class which is differentiated by the `CONDUIT.subtype` attribute. All conduit types have the same common
    attributes:

    **Common Attributes**

    Args:
        name (str): Conduit section name
        spill (str): Spill label
        comment (str): Comment included in unit
        dist_to_next (float): Distance to next section in metres
        subtype (str): Defines the type of conduit unit (*Should not be changed*)

    **Rectangular Type (``CONDUIT.subtype == 'RECTANGULAR'``)**

    Args:
        friction_eq (str): Friction equation to use (``'MANNING'`` or ``'COLEBROOK-WHITE'``)
        invert (float): Elevation of invert above datum (m)
        width (float): Width of conduit (m)
        height (float): Height of conduit (m)
        use_bottom_slot (str): Whether to include bottom slot (``'ON'``, ``'OFF'`` or ``'GLOBAL'``). Setting it to 'GLOBAL' will use the default option specified in IEF.
        bottom_slot_dist (float): Distance of slot top above invert (m)
        bottom_slot_depth (float): Total depth of bottom slot (m)
        use_top_slot (str): Whether to include top slot (``'ON'``, ``'OFF'`` or ``'GLOBAL'``). Setting it to 'GLOBAL' will use the default option specified in IEF.
        top_slot_dist (float): Distance of slot bottom below soffit (m)
        top_slot_depth (float): Total depth of top slot (m)
        friction_on_invert (float): Friction value for conduit invert
        friction_on_walls (float): Friction value for conduit walls
        friction_on_soffit (float): Friction value for conduit soffit

    **Circular Type (``CONDUIT.subtype == 'CIRCULAR'``)**

    Args:
        friction_eq (str): Friction equation to use (``'MANNING'`` or ``'COLEBROOK-WHITE'``)
        invert (float): Elevation of invert above datum (m)
        diameter (float): Diameter of conduit (m)
        use_bottom_slot (str): Whether to include bottom slot (``'ON'``, ``'OFF'`` or ``'GLOBAL'``). Setting it to 'GLOBAL' will use the default option specified in IEF.
        bottom_slot_dist (float): Distance of slot top above invert (m)
        bottom_slot_depth (float): Total depth of bottom slot (m)
        use_top_slot (str): Whether to include top slot (``'ON'``, ``'OFF'`` or ``'GLOBAL'``). Setting it to 'GLOBAL' will use the default option specified in IEF.
        top_slot_dist (float): Distance of slot bottom below soffit (m)
        top_slot_depth (float): Total depth of top slot (m)
        friction_below_axis (float): Friction value for conduit below axis
        friction_above_axis (float): Friction value for conduit above axis


    Raises:
        NotImplementedError: Raised if class is initialised without existing Conduit block (i.e. if attempting to create new
            Conduit unit). This will be an option for future releases

    Returns:
        CONDUIT: Flood Modeller CONDUIT Unit class object
    """

    _unit = "CONDUIT"

    def _read(self, c_block):
        """Function to read a given CONDUIT block and store data as class attributes"""
        self._subtype = c_block[1].split(" ")[0].strip()
        # Extends label line to be correct length before splitting to pick up blank labels
        labels = split_n_char(f"{c_block[2]:<{2*self._label_len}}", self._label_len)
        self.name = labels[0]
        self.spill = labels[1]
        self.comment = c_block[0].replace("CONDUIT", "").strip()

        # Read CIRCULAR type unit
        if self.subtype == "CIRCULAR":
            # Read Params
            self.dist_to_next = _to_float(split_10_char(c_block[3])[0])
            self.friction_eq = c_block[4].strip()
            params = split_10_char(f"{c_block[5]:<80}")
            self.invert = _to_float(params[0])
            self.diameter = _to_float(params[1])
            self.use_bottom_slot = _to_str(params[2], "GLOBAL")
            self.bottom_slot_dist = _to_float(params[3])
            self.bottom_slot_depth = _to_float(params[4])
            self.use_top_slot = _to_str(params[5], "GLOBAL")
            self.top_slot_dist = _to_float(params[6])
            self.top_slot_depth = _to_float(params[7])
            friction_params = split_10_char(f"{c_block[6]:<20}")
            self.friction_below_axis = _to_float(friction_params[0])
            self.friction_above_axis = _to_float(friction_params[1])

        elif self.subtype == "RECTANGULAR":
            # Read Params
            self.dist_to_next = _to_float(split_10_char(c_block[3])[0])
            self.friction_eq = c_block[4].strip()
            params = split_10_char(f"{c_block[5]:<90}")
            self.invert = _to_float(params[0])
            self.width = _to_float(params[1])
            self.height = _to_float(params[2])
            self.use_bottom_slot = _to_str(params[3], "GLOBAL")
            self.bottom_slot_dist = _to_float(params[4])
            self.bottom_slot_depth = _to_float(params[5])
            self.use_top_slot = _to_str(params[6], "GLOBAL")
            self.top_slot_dist = _to_float(params[7])
            self.top_slot_depth = _to_float(params[8])
            friction_params = split_10_char(f"{c_block[6]:<30}")
            self.friction_on_invert = _to_float(friction_params[0])
            self.friction_on_walls = _to_float(friction_params[1])
            self.friction_on_soffit = _to_float(friction_params[2])

        else:
            # This else block is triggered for conduit subtypes which aren't yet supported, and just keeps the '_block' in it's raw state to write back.
            print(
                f'This Conduit sub-type: "{self.subtype}" is currently unsupported for reading/editing'
            )
            self._raw_block = c_block

    def _write(self):
        """Function to write a valid CONDUIT block"""
        _validate_unit(self)  # Function to check the params are valid for CONDUIT unit
        header = "CONDUIT " + self.comment
        labels = join_n_char_ljust(self._label_len, self.name, self.spill)
        c_block = [header, self.subtype, labels]

        if self.subtype == "CIRCULAR":
            params = join_10_char(
                self.invert,
                self.diameter,
                self.use_bottom_slot,
                self.bottom_slot_dist,
                self.bottom_slot_depth,
                self.use_top_slot,
                self.top_slot_dist,
                self.top_slot_depth,
            )
            friction_params = (
                f"{self.friction_below_axis:>10.4f}{self.friction_above_axis:>10.4f}"
            )
            c_block.extend(
                [
                    f"{self.dist_to_next:>10.3f}",
                    self.friction_eq,
                    params,
                    friction_params,
                ]
            )
            return c_block

        elif self.subtype == "RECTANGULAR":
            params = join_10_char(
                self.invert,
                self.width,
                self.height,
                self.use_bottom_slot,
                self.bottom_slot_dist,
                self.bottom_slot_depth,
                self.use_top_slot,
                self.top_slot_dist,
                self.top_slot_depth,
            )
            friction_params = f"{self.friction_on_invert:>10.4f}{self.friction_on_walls:>10.4f}{self.friction_on_soffit:>10.4f}"
            c_block.extend(
                [
                    f"{self.dist_to_next:>10.3f}",
                    self.friction_eq,
                    params,
                    friction_params,
                ]
            )
            return c_block

        else:
            return self._raw_block
