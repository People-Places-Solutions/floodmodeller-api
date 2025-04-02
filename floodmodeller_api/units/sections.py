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

from __future__ import annotations

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
)
from .conveyance import calculate_cross_section_conveyance_cached


class RIVER(Unit):
    """Class to hold and process RIVER unit type. Currently only river units that are 'SECTION' types are supported.
    Other river unit types such as Muskingham will be included in a future release.

    Args:
        name (str, optional): River section name
        comment (str, optional): Comment included in unit
        data (pandas.Dataframe): Dataframe object containing all the cross section data as well as all other relevant data.
            Columns are ``'X', 'Y', 'Mannings n', 'Panel', 'RPL', 'Marker', 'Easting', 'Northing', 'Deactivation', 'SP. Marker'``
        spill1, spill2 (str, optional): Spill label
        lat1, lat2, lat3, lat4 (str, optional): Lateral inflow label
        dist_to_next (float, optional): Distance to next section in metres
        slope (float, optional): Slope used in normal depth calculations
        density (float, optional): Density in kg/m3

    Raises:
        NotImplementedError: Raised if class is initialised without existing river block (i.e. if attempting to create new River unit).
            This will be an option for future releases

    Returns:
        RIVER: Flood Modeller RIVER Unit class object
    """

    _unit = "RIVER"
    _required_columns = (
        "X",
        "Y",
        "Mannings n",
        "Panel",
        "RPL",
        "Marker",
        "Easting",
        "Northing",
        "Deactivation",
        "SP. Marker",
    )

    def _create_from_blank(  # noqa: PLR0913
        self,
        name="new_section",
        comment="",
        spill1="",
        spill2="",
        lat1="",
        lat2="",
        lat3="",
        lat4="",
        dist_to_next=0,
        slope=0.0001,
        density=1000.0,
        data=None,
    ):
        # Initiate new SECTION (currently hardcoding this as default)
        self._subtype = "SECTION"

        for param, val in {
            "name": name,
            "comment": comment,
            "spill1": spill1,
            "spill2": spill2,
            "lat1": lat1,
            "lat2": lat2,
            "lat3": lat3,
            "lat4": lat4,
            "dist_to_next": dist_to_next,
            "slope": slope,
            "density": density,
        }.items():
            setattr(self, param, val)

        self._data = self._enforce_dataframe(data, self._required_columns)
        self._active_data = None

    def _read(self, riv_block):
        """Function to read a given RIVER block and store data as class attributes."""

        self._subtype = riv_block[1].split(" ")[0].strip()
        # Extends label line to be correct length before splitting to pick up blank labels
        labels = split_n_char(f"{riv_block[2]:<{7 * self._label_len}}", self._label_len)

        # Only supporting 'SECTION' subtype for now
        if self.subtype == "SECTION":
            self.name = labels[0]
            self.spill1 = labels[1]
            self.spill2 = labels[2]
            self.lat1 = labels[3]
            self.lat2 = labels[4]
            self.lat3 = labels[5]
            self.lat4 = labels[6]
            self.comment = self._remove_unit_name(riv_block[0])

            params = split_10_char(f"{riv_block[3]:<40}")
            self.dist_to_next = to_float(params[0])
            self.slope = to_float(params[2], 0.0001)
            self.density = to_float(params[3], 1000.0)
            self.nrows = int(split_10_char(riv_block[4])[0])
            data_list = []
            for row in riv_block[5:]:
                row_split = split_10_char(f"{row:<100}")
                x = to_float(row_split[0])  # chainage
                y = to_float(row_split[1])  # elevation
                n = to_float(row_split[2])  # Mannings
                try:
                    # panel marker
                    panel = row_split[3][0] == "*"
                except IndexError:
                    panel = False

                try:
                    # relative path length
                    rpl = to_float(row_split[3][1 if panel else 0 :].strip())
                except IndexError:
                    rpl = 0.000
                marker = row_split[4]  # Marker
                easting = to_float(row_split[5])  # easting
                northing = to_float(row_split[6])  # northing

                deactivation = row_split[7]  # deactivation marker
                sp_marker = to_int(row_split[8])  # special marker
                data_list.append(
                    [
                        x,
                        y,
                        n,
                        panel,
                        rpl,
                        marker,
                        easting,
                        northing,
                        deactivation,
                        sp_marker,
                    ],
                )
            self._data = pd.DataFrame(
                data_list,
                columns=self._required_columns,
            )

        else:
            # This else block is triggered for river subtypes which aren't yet supported, and just keeps the 'riv_block' in it's raw state to write back.
            logging.warning(
                "This River sub-type: '%s' is currently unsupported for reading/editing",
                self.subtype,
            )
            self._raw_block = riv_block
            self.name = riv_block[2][: self._label_len].strip()
            self.dist_to_next = to_float(riv_block[3][:10])
            self.labels = labels

        self._active_data = None

    def _write(self):
        """Function to write a valid RIVER block"""

        if self.subtype == "SECTION":
            # Function to check the params are valid for RIVER SECTION unit
            _validate_unit(self)
            header = self._create_header()
            labels = join_n_char_ljust(
                self._label_len,
                self.name,
                self.spill1,
                self.spill2,
                self.lat1,
                self.lat2,
                self.lat3,
                self.lat4,
            )
            # Manual so slope can have more sf
            params = f"{self.dist_to_next:>10.3f}{'':>10}{self.slope:>10.6f}{self.density:>10.3f}"
            self.nrows = len(self._data)
            riv_block = [header, self.subtype, labels, params, f"{self.nrows!s:>10}"]

            riv_data = []
            for (
                _,
                x,
                y,
                n,
                panel,
                rpl,
                marker,
                easting,
                northing,
                deactivation,
                sp_marker,
            ) in self._data.itertuples():
                row = join_10_char(x, y, n)
                if panel:
                    row += "*"
                else:
                    row += " "
                row += f"{rpl:>9.3f}{join_10_char(marker, easting, northing, deactivation, str(sp_marker))}"
                riv_data.append(row)

            riv_block.extend(riv_data)

            return riv_block

        return self._raw_block

    @property
    def data(self) -> pd.DataFrame:
        """Data table for the river cross section.

        Returns:
            pd.DataFrame: Pandas dataframe for the cross section data with columns: 'X', 'Y',
            'Mannings n', 'Panel', 'RPL', 'Marker', 'Easting', 'Northing', 'Deactivation',
            'SP. Marker'
        """
        if self._active_data is None:
            return self._data

        # Replace the active section with the self._active_data df
        left_bank_idx, right_bank_idx = self._get_left_right_active_index()
        self._data = pd.concat(
            [self._data[:left_bank_idx], self._active_data, self._data[right_bank_idx + 1 :]],
        ).reset_index(drop=True)
        self._active_data = None
        return self._data

    @data.setter
    def data(self, new_df: pd.DataFrame) -> None:
        if not isinstance(new_df, pd.DataFrame):
            msg = "The updated data table for a cross section must be a pandas DataFrame."
            raise ValueError(msg)
        if list(map(str.lower, new_df.columns)) != list(map(str.lower, self._required_columns)):
            msg = f"The DataFrame must only contain columns: {self._required_columns}"
            raise ValueError(msg)
        self._data = new_df

    @property
    def conveyance(self) -> pd.Series:
        """Calculate and return the conveyance curve of the cross-section.

        Note:
            This uses the same method as applied in Flood Modeller so will be able to pick out any
            undesirable spikes in conveyance. The only difference compared with Flood Modeller may
            be the number of sampled points.

        Returns:
            pd.Series: A pandas Series containing the conveyance values indexed by water levels.
        """
        return calculate_cross_section_conveyance_cached(
            x=tuple(self._data.X.values),
            y=tuple(self._data.Y.values),
            n=tuple(self._data["Mannings n"].values),
            rpl=tuple(self._data.RPL.values),
            panel_markers=tuple(self._data.Panel.values),
        )

    @property
    def active_data(self) -> pd.DataFrame:
        """Data table for active subset of the river cross section, defined by deactivation markers.

        Returns:
            pd.DataFrame: Pandas dataframe for the active cross section data with columns: 'X', 'Y',
            'Mannings n', 'Panel', 'RPL', 'Marker', 'Easting', 'Northing', 'Deactivation',
            'SP. Marker'

        Example:
            In this example we read in a river section that has deactivation markers

            .. ipython:: python

                from floodmodeller_api.units import RIVER
                river_unit = RIVER(
                    [
                        "RIVER normal case",
                        "SECTION",
                        "SomeUnit",
                        "     0.000            0.000100  1000.000",
                        "        5",
                        "     0.000        10     0.030     0.000                 0.0       0.0          ",
                        "     1.000         9     0.030     0.000                 0.0       0.0      LEFT",
                        "     2.000         5     0.030     0.000                 0.0       0.0          ",
                        "     3.000         6     0.030     0.000                 0.0       0.0     RIGHT",
                        "     4.000        10     0.030     0.000                 0.0       0.0          ",
                    ]
                )
                river_unit.data
                river_unit.active_data
        """
        if self._active_data is not None:
            return self._active_data
        left_bank_idx, right_bank_idx = self._get_left_right_active_index()
        self._active_data = self._data.iloc[left_bank_idx : right_bank_idx + 1].copy()
        return self._active_data

    @active_data.setter
    def active_data(self, new_df: pd.DataFrame) -> None:
        if not isinstance(new_df, pd.DataFrame):
            msg = "The updated data table for a cross section must be a pandas DataFrame."
            raise ValueError(msg)
        if new_df.columns.to_list() != self._required_columns:
            msg = f"The DataFrame must only contain columns: {self._required_columns}"
            raise ValueError(msg)

        # Ensure activation markers are present
        new_df = new_df.copy()
        new_df.iloc[0, 8] = "LEFT"
        new_df.iloc[-1, 8] = "RIGHT"
        self._active_data = new_df

    def _get_left_right_active_index(self) -> tuple[int, int]:
        bank_data = self._data.Deactivation.to_list()
        lb_flag = "LEFT" in bank_data
        rb_flag = "RIGHT" in bank_data

        left_bank_idx = (len(bank_data) - 1) - bank_data[::-1].index("LEFT") if lb_flag else 0
        right_bank_idx = bank_data.index("RIGHT") if rb_flag else len(bank_data) - 1
        return left_bank_idx, right_bank_idx


class INTERPOLATE(Unit):
    """Class to hold and process INTERPOLATE unit type

    Args:
        name (str, optional): Unit name.
        comment (str, optional): Comment included in unit.
        first_spill (str, optional): Spill label if required.
        second_spill (str, optional): Spill label if required.
        lat1 (str, optional): First lateral inflow label.
        lat2 (str, optional): Second lateral inflow label.
        lat3 (str, optional): Third lateral inflow label.
        lat4 (str, optional): Fourth lateral inflow label.
        dist_to_next (float, optional): Chainage downstream to following section (m).
        easting (float, optional): Easting coordinate of interpolated section (not used in hydraulic calculations).
        northing (float, optional): Northing coordinate of interpolated section (not used in hydraulic calculations).

    Returns:
        INTERPOLATE: Flood Modeller INTERPOLATE Unit class object"""

    _unit = "INTERPOLATE"

    def _read(self, block):
        """Function to read a given INTERPOLATE WEIR block and store data as class attributes"""

        # Extends label line to be correct length before splitting to pick up blank labels
        labels = split_n_char(f"{block[1]:<{7 * self._label_len}}", self._label_len)
        self.name = labels[0]
        self.first_spill = labels[1]
        self.second_spill = labels[2]
        self.lat1 = labels[3]
        self.lat2 = labels[4]
        self.lat3 = labels[5]
        self.lat4 = labels[6]
        self.comment = self._remove_unit_name(block[0])

        # First parameter line
        params1 = split_10_char(f"{block[2]:<30}")
        self.dist_to_next = to_float(params1[0])
        self.easting = to_float(params1[1])
        self.northing = to_float(params1[2])

    def _write(self):
        """Function to write a valid INTERPOLATE block"""

        _validate_unit(self)
        header = self._create_header()
        labels = join_n_char_ljust(
            self._label_len,
            self.name,
            self.first_spill,
            self.second_spill,
            self.lat1,
            self.lat2,
            self.lat3,
            self.lat4,
        )
        block = [header, labels]

        # First parameter line
        params1 = join_10_char(self.dist_to_next, self.easting, self.northing)
        block.append(params1)

        return block

    def _create_from_blank(  # noqa: PLR0913
        self,
        name="new_interp",
        comment="",
        first_spill="",
        second_spill="",
        lat1="",
        lat2="",
        lat3="",
        lat4="",
        dist_to_next=0,
        easting=0,
        northing=0,
    ):
        for param, val in {
            "name": name,
            "comment": comment,
            "first_spill": first_spill,
            "second_spill": second_spill,
            "lat1": lat1,
            "lat2": lat2,
            "lat3": lat3,
            "lat4": lat4,
            "dist_to_next": dist_to_next,
            "easting": easting,
            "northing": northing,
        }.items():
            setattr(self, param, val)


class REPLICATE(Unit):
    """Class to hold and process REPLICATE unit type

    Args:
        name (str, optional): Unit name.
        comment (str, optional): Comment included in unit.
        first_spill (str, optional): Spill label if required.
        second_spill (str, optional): Spill label if required.
        lat1 (str, optional): First lateral inflow label.
        lat2 (str, optional): Second lateral inflow label.
        lat3 (str, optional): Third lateral inflow label.
        lat4 (str, optional): Fourth lateral inflow label.
        dist_to_next (float, optional): Chainage downstream to following section (m).
        easting (float, optional): Easting coordinate of interpolated section (not used in hydraulic calculations).
        northing (float, optional): Northing coordinate of interpolated section (not used in hydraulic calculations).
        bed_level_drop (float, optional): Drop in bed level from previous section (m).

    Returns:
        REPLICATE: Flood Modeller REPLICATE Unit class object"""

    _unit = "REPLICATE"

    def _read(self, block: list[str]):
        """Function to read a given REPLICATE block and store data as class attributes"""

        # Extends label line to be correct length before splitting to pick up blank labels
        labels = split_n_char(f"{block[1]:<{7 * self._label_len}}", self._label_len)
        self.name = labels[0]
        self.first_spill = labels[1]
        self.second_spill = labels[2]
        self.lat1 = labels[3]
        self.lat2 = labels[4]
        self.lat3 = labels[5]
        self.lat4 = labels[6]

        self.comment = self._remove_unit_name(block[0])

        # First parameter line
        params1 = split_10_char(f"{block[2]:<40}")
        self.dist_to_next = to_float(params1[0])
        self.bed_level_drop = to_float(params1[1])
        self.easting = to_float(params1[2])
        self.northing = to_float(params1[3])

    def _write(self):
        """Function to write a valid REPLICATE block"""

        _validate_unit(self)
        header = self._create_header()
        labels = join_n_char_ljust(
            self._label_len,
            self.name,
            self.first_spill,
            self.second_spill,
            self.lat1,
            self.lat2,
            self.lat3,
            self.lat4,
        )
        block = [header, labels]

        # First parameter line

        params1 = join_10_char(
            self.dist_to_next,
            f"{self.bed_level_drop:>10.4f}",  # allowing 4dp
            self.easting,
            self.northing,
        )
        block.append(params1)

        return block

    def _create_from_blank(  # noqa: PLR0913
        self,
        name="new_repl",
        comment="",
        first_spill="",
        second_spill="",
        lat1="",
        lat2="",
        lat3="",
        lat4="",
        dist_to_next=0,
        bed_level_drop=0,
        easting=0,
        northing=0,
    ):
        for param, val in {
            "name": name,
            "comment": comment,
            "first_spill": first_spill,
            "second_spill": second_spill,
            "lat1": lat1,
            "lat2": lat2,
            "lat3": lat3,
            "lat4": lat4,
            "dist_to_next": dist_to_next,
            "bed_level_drop": bed_level_drop,
            "easting": easting,
            "northing": northing,
        }.items():
            setattr(self, param, val)
