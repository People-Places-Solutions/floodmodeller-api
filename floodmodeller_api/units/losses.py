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
    to_data_list,
    to_float,
    to_int,
    to_str,
)


class CULVERT(Unit):
    """The CULVERT class supports two culvert sub-types in Flood Modeller: INLET and OUTLET. Each of these sub-types forms
    a unique instance of the class which is differentiated by the ``CULVERT.subtype`` attribute. Physical culvert types (e.g. rectangualr, circular etc)
    are provided under the CONDUIT class for consistency with Flood Modeller.

    **Common attributes**

    Args:
        name (str): Unit name and upstream node label
        ds_label (str): Downstream node label
        us_remote_label (str): Upstream remote node label
        ds_remote_label (str): Downstream remote node label
        comment (str): Comment
        loss_coefficient (float): Loss coefficient.  Outlet (default = 1.0), INLET (Trash screen head loss coefficient, default = 1.5)
        headloss_type (str): Keyword TOTAL to denote headloss based on total head, otherwise (keyword STATIC or blank) headloss is based on static head
        reverse_flow_mode (str): Reverse Flow Mode; keyword ZERO (for zero headloss in reverse flow) or CALCULATED (for calculated head loss in reverse flow)

    **Inlet Loss Type** (``CULVERT.subtype == 'INLET'``)

    Args:
        type_code (str): options are 'Type A', 'Type B','Type C'
        k (float): Unsubmerged inlet control loss coefficient
        m (float): Exponent of Flow Intensity for inlet control
        c (float): Submerged inlet control loss coefficient
        y (float): Submerged inlet control adjustment factor
        ki (float): Outlet control loss coefficient
        screen_width (float): Trash screen width (m)
        bar_proportion (float): Proportion of trash screen area occupied by bars (0 to 1.0)
        debris_proportion (float): Blockage ratio (proportion of trash screen area occupied by debris) (0 to 1.0)
        max_screen_height (float): Max. Trash Screen Height (see Flood Modeller help for further information)

    **Outlet Loss Type** (``CULVERT.subtype == 'OUTLET'``)

    No additional attributes required for OUTLET subtype

    Returns:
        CULVERT: Flood Modeller CULVERT unit class object
    """

    _unit = "CULVERT"

    def _read(self, block):
        """Function to read a given CULVERT block and store data as class attributes"""

        # Extract common attributes
        self._subtype = block[1].split(" ")[0].strip()
        self.comment = block[0].replace("CULVERT", "").strip()
        labels = split_n_char(f"{block[2]:<{4*self._label_len}}", self._label_len)
        self.name = labels[0]
        self.ds_label = labels[1]
        self.us_remote_label = labels[2]
        self.ds_remote_label = labels[3]

        # Extract subtype specific attributes

        if self.subtype == "INLET":
            # Defaults applied are equivellent to those provide if Culvert Wizard cancelled.

            # Read first set of general parameters
            params = split_10_char(f"{block[3]:<60}")
            self.k = to_float(params[0], 0.0)
            self.m = to_float(params[1], 0.0)
            self.c = to_float(params[2], 0.0)
            self.y = to_float(params[3], 0.0)
            self.ki = to_float(params[4], 0.0)
            self.type_code = to_str(params[5], "A")

            # Read trash screen and remaining general parameters
            params1 = split_10_char(f"{block[4]:<70}")
            self.screen_width = to_float(params1[0], 0.0)
            self.bar_proportion = to_float(params1[1], 0.0)
            self.debris_proportion = to_float(params1[2], 0.0)
            self.loss_coefficient = to_float(params1[3], 0.0)
            self.reverse_flow_mode = to_str(params1[4], "CALCULATED", check_float=True)
            self.headloss_type = to_str(params1[5], "TOTAL")
            self.max_screen_height = to_float(params1[6], 0.0)

        elif self.subtype == "OUTLET":
            params = split_10_char(f"{block[3]:<30}")
            self.loss_coefficient = to_float(params[0], 1.0)
            self.reverse_flow_mode = to_str(params[1], "CALCULATED")
            self.headloss_type = to_str(params[2], "TOTAL")

        else:
            # This else block is triggered for culvert subtypes which aren't yet supported, and just keeps the '_block' in its raw state to write back.
            logging.warning(
                "This Culvert sub-type: '%s' is currently unsupported for reading/editing",
                self.subtype,
            )
            self._raw_block = block

    def _write(self):
        """Function to write a valid CULVERT block"""

        _validate_unit(self)

        header = "CULVERT " + self.comment
        labels = join_n_char_ljust(
            self._label_len,
            self.name,
            self.ds_label,
            self.us_remote_label,
            self.ds_remote_label,
        )
        c_block = [header, self.subtype, labels]

        if self.subtype == "INLET":
            params = join_10_char(self.k, self.m, self.c, self.y, self.ki, self.type_code, dp=4)
            params1 = join_10_char(
                self.screen_width,
                self.bar_proportion,
                self.debris_proportion,
                self.loss_coefficient,
                self.reverse_flow_mode,
                self.headloss_type,
                self.max_screen_height,
                dp=4,
            )

            c_block.extend([params, params1])

            return c_block

        if self.subtype == "OUTLET":
            params = join_10_char(self.loss_coefficient, self.reverse_flow_mode, self.headloss_type)

            c_block.append(params)
            return c_block

        return self._raw_block


class BLOCKAGE(Unit):
    """Class to hold and process BLOCKAGE unit type.

    Args:
        comment (str): Comment included in unit.
        name (str): Upstream label name
        ds_label (str): Downstream label
        us_reference_label (str): Upstream reference label
        ds_reference_label (str): Downstream reference label
        constriction_label (str): Constriction reference label
        inlet_loss (float): Inlet loss coefficient
        outlet_loss (float): Outlet loss coefficient
        timeoffset (float): Time Datum Adjustment
        timeunit_blockage (str): Unit of time, e.g. 'HOURS', 'MINUTES' or 'SECONDS'. See Flood Modeller documentation for all available options.
        extendmethod (str): Data extending method: 'EXTEND', 'NOEXTEND' or 'REPEAT'. Defaults to None.
        data (pandas.Series): Series object with variable ``'blockage'`` and index ``'Time'``. Defaults to None.


    Returns:
        BLOCKAGE: Flood Modeller BLOCAKGE Unit class object
    """

    _unit = "BLOCKAGE"

    def _read(self, block):
        """Function to read a given BLOCKAGE block and store data as class attributes"""

        # Extract comment and revision number
        b = block[0].replace("BLOCKAGE #revision#", " ").strip()
        self._revision = to_int(b[0], 1)
        self.comment = b[1:].strip()

        # Extract labels
        labels = split_n_char(f"{block[1]:<{5*self._label_len}}", self._label_len)
        self.name = labels[0]
        self.ds_label = labels[1]
        self.us_reference_label = labels[2]
        self.ds_reference_label = labels[3]
        self.constriction_label = labels[4]

        # Extract inlet and outlet loss coefficients
        params = split_10_char(f"{block[2]:<20}")
        self.inlet_loss = to_float(params[0], 1.5)
        self.outlet_loss = to_float(params[1], 1.0)

        # Extract blockage timeseries parameters
        params1 = split_10_char(f"{block[3]:<40}")
        self.nrows = int(params1[0])
        self.timeoffset = to_float(params1[1])

        self.timeunit = to_str(params1[2], "HOURS", check_float=True)
        if self.timeunit == "DATE":
            self.timeunit = "DATES"  # Parameter value updated to 'DATES' for consistency with other unit types.  'DATE' and 'DATES' both accepted for blockage unit ONLY

        self.extendmethod = to_str(params1[3], "NOEXTEND")

        # Extract blockage to timeseries
        data_list = (
            to_data_list(block[4:], num_cols=2, date_col=0)
            if self.timeunit == "DATES"
            else to_data_list(block[4:], num_cols=2)
        )  # Enforced two columns as Flood Modeller saves old parameters when using DATES (also to avoid extra 'HOURS' bug)

        self.data = pd.DataFrame(data_list, columns=["Time", "Blockage"])
        self.data = self.data.set_index("Time")
        self.data = self.data["Blockage"]

    def _write(self):
        """Function to write a valid BLOCKAGE block"""

        _validate_unit(self)

        # Custom validation for blockage percentage
        if self.data.max() > 1 or self.data.min() < 0:
            msg = f"Parameter error with {self!r} - blockage percentage must be between 0 and 1"
            raise ValueError(msg)

        header = f"BLOCKAGE #revision#{self._revision} {self.comment}"
        labels = join_n_char_ljust(
            self._label_len,
            self.name,
            self.ds_label,
            self.us_reference_label,
            self.ds_reference_label,
            self.constriction_label,
        )
        params = join_10_char(self.inlet_loss, self.outlet_loss)
        self.nrows = len(self.data)
        params1 = join_10_char(self.nrows, self.timeoffset, self.timeunit, self.extendmethod)

        blockage_block = [header, labels, params, params1]

        if self.timeunit == "DATES":
            blockage_data = [f"{t:<20}{join_10_char(b)}" for t, b in self.data.items()]
        else:
            blockage_data = [join_10_char(t, b) for t, b in self.data.items()]

        blockage_block.extend(blockage_data)

        return blockage_block

    def _create_from_blank(  # noqa: PLR0913
        self,
        name="new_blockage",
        _revision=1,
        comment="",
        ds_label="",
        us_reference_label="",
        ds_reference_label="",
        constriction_label="",
        inlet_loss=1.5,
        outlet_loss=1.0,
        timeoffset=0.0,
        timeunit="HOURS",
        extendmethod="EXTEND",
        data=None,
    ):
        # Initiate new BLOCKAGE unit
        for param, val in {
            "name": name,
            "_revision": _revision,
            "comment": comment,
            "ds_label": ds_label,
            "us_reference_label": us_reference_label,
            "ds_reference_label": ds_reference_label,
            "constriction_label": constriction_label,
            "inlet_loss": inlet_loss,
            "outlet_loss": outlet_loss,
            "timeoffset": timeoffset,
            "timeunit": timeunit,
            "extendmethod": extendmethod,
            "data": data,
        }.items():
            setattr(self, param, val)

        self.data = (
            data if isinstance(data, pd.Series) else pd.Series([0.0], index=[0.0], name="Blockage")
        )
