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

import logging

import pandas as pd

from floodmodeller_api.validation import _validate_unit

from ._base import Unit
from ._helpers import (
    join_10_char,
    join_n_char_ljust,
    split_10_char,
    split_n_char,
    to_float,
    to_int,
    to_str,
)


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

    **Sprung Type (``CONDUIT.subtype == 'SPRUNG'``)**

    Args:
        equation (str): Choose between the Manning's formulation and the Colbrook-White's formulation
        elevation_invert (float): Height of the conduit above datum (m)
        width (float): Width of conduit (m)
        height_springing (float): Height of conduit's springing (m)
        height_crown (float): Height of conduit's crown (m)
        use_bottom_slot (str): Whether to include bottom slot (``'ON'``, ``'OFF'`` or ``'GLOBAL'``). Setting it to 'GLOBAL' will use the default option specified in IEF.
        bottom_slot_dist (float): Distance of slot top above invert (m)
        bottom_slot_depth (float): Total depth of bottom slot (m)
        use_top_slot (str): Whether to include top slot (``'ON'``, ``'OFF'`` or ``'GLOBAL'``). Setting it to 'GLOBAL' will use the default option specified in IEF.
        top_slot_dist (float): Distance of slot bottom below soffit (m)
        top_slot_depth (float): Total depth of top slot (m)
        friction_on_invert (float): Friction value for conduit invert
        friction_on_walls (float): Friction value for conduit walls
        friction_on_soffit (float): Friction value for conduit soffit

    **Sprungarch Type (``CONDUIT.subtype == 'SPRUNGARCH'``)**

    Args:
        equation (str): Choose between the Manning's formulation and the Colbrook-White's formulation
        elevation_invert (float): Height of the conduit above datum (m)
        width (float): Width of conduit (m)
        height_springing (float): Height of conduit's springing (m)
        height_crown (float): Height of conduit's crown (m)
        use_bottom_slot (str): Whether to include bottom slot (``'ON'``, ``'OFF'`` or ``'GLOBAL'``). Setting it to 'GLOBAL' will use the default option specified in IEF.
        bottom_slot_dist (float): Distance of slot top above invert (m)
        bottom_slot_depth (float): Total depth of bottom slot (m)
        use_top_slot (str): Whether to include top slot (``'ON'``, ``'OFF'`` or ``'GLOBAL'``). Setting it to 'GLOBAL' will use the default option specified in IEF.
        top_slot_dist (float): Distance of slot bottom below soffit (m)
        top_slot_depth (float): Total depth of top slot (m)
        friction_on_invert (float): Friction value for conduit invert
        friction_on_walls (float): Friction value for conduit walls
        friction_on_soffit (float): Friction value for conduit soffit

    **Section Type (``CONDUIT.subtype == 'SECTION'``)**

    Args:
        None - common args attributes only

    Raises:
        NotImplementedError: Raised if class is initialised without existing Conduit block (i.e. if attempting to create new
            Conduit unit). This will be an option for future releases

    Returns:
        CONDUIT: Flood Modeller CONDUIT Unit class object
    """

    _unit = "CONDUIT"

    def _create_from_blank(  # noqa: PLR0913
        self,
        name="new_unit",
        spill="",
        comment="",
        dist_to_next=0.0,
        subtype="SECTION",
        friction_eq="MANNING",
        invert=0.0,
        width=0.0,
        height=0.0,
        use_bottom_slot="GLOBAL",
        bottom_slot_dist=0.0,
        bottom_slot_depth=0.0,
        use_top_slot="GLOBAL",
        top_slot_dist=0.0,
        top_slot_depth=0.0,
        friction_on_invert=0.0,
        friction_on_walls=0.0,
        friction_on_soffit=0.0,
        diameter=0.0,
        friction_above_axis=0.0,
    ):
        for param, val in {
            "name": name,
            "spill": spill,
            "comment": comment,
            "dist_to_next": dist_to_next,
            "subtype": subtype,
            "friction_eq": friction_eq,
            "invert": invert,
            "width": width,
            "height": height,
            "use_bottom_slot": use_bottom_slot,
            "bottom_slot_dist": bottom_slot_dist,
            "bottom_slot_depth": bottom_slot_depth,
            "use_top_slot": use_top_slot,
            "top_slot_dist": top_slot_dist,
            "top_slot_depth": top_slot_depth,
            "friction_on_invert": friction_on_invert,
            "friction_on_walls": friction_on_walls,
            "friction_on_soffit": friction_on_soffit,
            "diameter": diameter,
            "friction_above_axis": friction_above_axis,
        }.items():
            if param == "subtype":
                self._subtype = val
            else:
                setattr(self, param, val)

    def _read(self, c_block):  # noqa: PLR0915
        """Function to read a given CONDUIT block and store data as class attributes"""
        self._subtype = self._get_first_word(c_block[1])
        # Extends label line to be correct length before splitting to pick up blank labels
        labels = split_n_char(f"{c_block[2]:<{2*self._label_len}}", self._label_len)
        self.name = labels[0]
        self.spill = labels[1]
        self.comment = self._remove_unit_name(c_block[0])

        # Read CIRCULAR type unit
        if self._subtype == "CIRCULAR":
            # Read Params
            self.dist_to_next = to_float(split_10_char(c_block[3])[0])
            self.friction_eq = c_block[4].strip()
            params = split_10_char(f"{c_block[5]:<80}")
            self.invert = to_float(params[0])
            self.diameter = to_float(params[1])
            self.use_bottom_slot = to_str(params[2], "GLOBAL")
            self.bottom_slot_dist = to_float(params[3])
            self.bottom_slot_depth = to_float(params[4])
            self.use_top_slot = to_str(params[5], "GLOBAL")
            self.top_slot_dist = to_float(params[6])
            self.top_slot_depth = to_float(params[7])
            friction_params = split_10_char(f"{c_block[6]:<20}")
            self.friction_below_axis = to_float(friction_params[0])
            self.friction_above_axis = to_float(friction_params[1])

        elif self._subtype == "RECTANGULAR":
            # Read Params
            self.dist_to_next = to_float(split_10_char(c_block[3])[0])
            self.friction_eq = c_block[4].strip()
            params = split_10_char(f"{c_block[5]:<90}")
            self.invert = to_float(params[0])
            self.width = to_float(params[1])
            self.height = to_float(params[2])
            self.use_bottom_slot = to_str(params[3], "GLOBAL")
            self.bottom_slot_dist = to_float(params[4])
            self.bottom_slot_depth = to_float(params[5])
            self.use_top_slot = to_str(params[6], "GLOBAL")
            self.top_slot_dist = to_float(params[7])
            self.top_slot_depth = to_float(params[8])
            friction_params = split_10_char(f"{c_block[6]:<30}")
            self.friction_on_invert = to_float(friction_params[0])
            self.friction_on_walls = to_float(friction_params[1])
            self.friction_on_soffit = to_float(friction_params[2])

        elif self._subtype in ("SPRUNG", "SPRUNGARCH"):
            self.dist_to_next = to_float(split_10_char(c_block[3])[0])
            self.equation = to_str(c_block[4], "MANNING")
            params = split_10_char(f"{c_block[5]:<100}")
            self.elevation_invert = to_float(params[0])
            self.width = to_float(params[1])
            self.height_springing = to_float(params[2])
            self.height_crown = to_float(params[3])
            self.use_bottom_slot = to_str(params[4], "GLOBAL")
            self.bottom_slot_dist = to_float(params[5])
            self.bottom_slot_depth = to_float(params[6])
            self.use_top_slot = to_str(params[7], "GLOBAL")
            self.top_slot_dist = to_float(params[8])
            self.top_slot_depth = to_float(params[9])
            friction_params = split_10_char(f"{c_block[6]:<30}")
            self.friction_on_invert = to_float(friction_params[0])
            self.friction_on_walls = to_float(friction_params[1])
            self.friction_on_soffit = to_float(friction_params[2])

        elif self._subtype == "SECTION":
            self.dist_to_next = to_float(split_10_char(c_block[3])[0])
            end_index = 5 + to_int(c_block[4])
            x = []
            y = []
            friction = []
            for i in range(5, end_index):
                row_data = split_10_char(f"{c_block[i]:<30}")
                x.append(to_float(row_data[0]))
                y.append(to_float(row_data[1]))
                friction.append(to_float(row_data[2]))
            self.coords = pd.DataFrame({"x": x, "y": y, "cw_friction": friction})

        else:
            # This else block is triggered for conduit subtypes which aren't yet supported, and just keeps the '_block' in it's raw state to write back.
            logging.warning(
                "This Conduit sub-type: '%s' is currently unsupported for reading/editing",
                self._subtype,
            )
            self._raw_block = c_block

    def _write(self):
        """Function to write a valid CONDUIT block"""
        _validate_unit(self)  # Function to check the params are valid for CONDUIT unit
        header = self._create_header()
        labels = join_n_char_ljust(self._label_len, self.name, self.spill)
        c_block = [header, self._subtype, labels]

        if self._subtype == "CIRCULAR":
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
            friction_params = f"{self.friction_below_axis:>10.4f}{self.friction_above_axis:>10.4f}"
            c_block.extend(
                [
                    f"{self.dist_to_next:>10.3f}",
                    self.friction_eq,
                    params,
                    friction_params,
                ],
            )
            return c_block

        if self._subtype == "RECTANGULAR":
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
                ],
            )
            return c_block

        if self._subtype == "SPRUNG":
            c_block.extend(
                [
                    str(self.dist_to_next),
                    self.equation,
                    join_10_char(
                        self.elevation_invert,
                        self.width,
                        self.height_springing,
                        self.height_crown,
                        self.use_bottom_slot,
                        self.bottom_slot_dist,
                        self.bottom_slot_depth,
                        self.use_top_slot,
                        self.top_slot_dist,
                        self.top_slot_depth,
                    ),
                    join_10_char(
                        self.friction_on_invert,
                        self.friction_on_walls,
                        self.friction_on_soffit,
                    ),
                ],
            )
            return c_block

        if self._subtype == "SPRUNGARCH":
            c_block.extend(
                [
                    str(self.dist_to_next),
                    self.equation,
                    join_10_char(
                        self.elevation_invert,
                        self.width,
                        self.height_springing,
                        self.height_crown,
                        self.use_bottom_slot,
                        self.bottom_slot_dist,
                        self.bottom_slot_depth,
                        self.use_top_slot,
                        self.top_slot_dist,
                        self.top_slot_depth,
                    ),
                    join_10_char(
                        self.friction_on_invert,
                        self.friction_on_walls,
                        self.friction_on_soffit,
                    ),
                ],
            )
            return c_block

        if self._subtype == "SECTION":
            c_block.extend(
                [
                    join_10_char(self.dist_to_next),
                    join_10_char(len(self.coords)),
                ],
            )
            for _, coord in self.coords.iterrows():
                c_block.extend(
                    [join_10_char(coord.x, coord.y) + join_10_char(coord.cw_friction, dp=6)],
                )
            return c_block

        return self._raw_block
