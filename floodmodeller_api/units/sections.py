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
    write_dataframe,
)
from .conveyance import calculate_cross_section_conveyance_cached


class RIVER(Unit):
    """Class to hold and process RIVER unit type. The RIVER class supports five river sub-types in Flood Modeller:
    SECTION, MUSKINGUM, MUSK-XSEC, MUSK-VPMC and MUSK-RSEC. Each of these sub-types forms a unique instance of the
    class which is differentiated by the ``RIVER.subtype`` attribute.

    **Common Attributes**

    Args:
        name (str, optional): River unit name
        comment (str, optional): Comment included in unit
        dist_to_next (float, optional): Distance to next section in metres
        subtype (str): Defines the type of river unit (*Should not be changed*)

    **Section Type (``RIVER.subtype == 'SECTION'``)**

    Args:
        spill1, spill2 (str, optional): Spill label
        lat1, lat2, lat3, lat4 (str, optional): Lateral inflow label.
        slope (float, optional): Slope used in normal depth calculations.
        density (float, optional): Density in kg/m3
        nrows (int): Number of cross section data rows.
        data (pandas.Dataframe): Dataframe object containing the cross section data. Columns are ``'X'``, ``'Y'``,
            ``'Mannings n'``, ``'Panel'``, ``'RPL'``, ``'Marker'``, ``'Easting'``, ``'Northing'``,
            ``'Deactivation'`` and ``'SP. Marker'``.
        active_data (pandas.Dataframe): Active subset of ``data`` between deactivation markers.

    **Muskingum Type (``RIVER.subtype == 'MUSKINGUM'``)**

    Args:
        bed_elevation (float): Bed elevation.
        k (float): Muskingum ``K`` parameter.
        x (float): Muskingum ``X`` parameter.

    **Muskingum Cross Section Type (``RIVER.subtype == 'MUSK-XSEC'``)**

    Args:
        first_lateral_inflow_node, second_lateral_inflow_node (str, optional): Lateral inflow node labels.
        lat1, lat2, lat3, lat4 (str, optional): Lateral inflow label.
        bed_elevation (float): Bed elevation.
        slope (float): Slope.
        min_subnodes, max_subnodes (int): Minimum and maximum number of subnodes.
        max_flow (float): Maximum flow.
        low_flow_smoothing_factor (float): Low flow smoothing factor.
        nrows (int): Number of cross section data rows.
        data (pandas.Dataframe): Dataframe object containing the cross section data. Columns are ``'X'``, ``'Y'``,
            ``'Mannings n'``, ``'Panel'``, ``'RPL'``, ``'Marker'``, ``'Easting'`` and ``'Northing'``.

    **Muskingum VPMC Type (``RIVER.subtype == 'MUSK-VPMC'``)**

    Args:
        first_lateral_inflow_node, second_lateral_inflow_node (str, optional): Lateral inflow node labels.
        lat1, lat2, lat3, lat4 (str, optional): Lateral inflow label.
        bed_elevation (float): Bed elevation.
        slope (float): Slope.
        min_subnodes, max_subnodes (int): Minimum and maximum number of subnodes.
        specified_discharge (float): Specified discharge.
        nrows (int): Number of wavespeed data rows.
        wavespeed_data (pandas.Dataframe): Dataframe object containing the VPMC data. Columns are ``'Flow'``,
            ``'Wavespeed'``, ``'Attenuation'`` and ``'Water Level'``.

    **Muskingum RSEC Type (``RIVER.subtype == 'MUSK-RSEC'``)**

    Args:
        first_lateral_inflow_node, second_lateral_inflow_node (str, optional): Lateral inflow node labels.
        lat1, lat2, lat3, lat4 (str, optional): Lateral inflow label.
        bed_elevation (float): Bed elevation.
        roughness_type (str): Roughness type.
        channel_roughness, floodplain_roughness (float): Channel and floodplain roughness values.
        channel_slope, floodplain_slope (float): Channel and floodplain slopes.
        b1, b2, b3, b4 (float): ``b`` parameters.
        d1, d2, d3, d4 (float): ``d`` parameters.
        vs (float): ``vs`` parameter.
        max_flow (float): Maximum flow.
        bankfull_proportion (float): Bankfull proportion.

    **Velocity Method Attributes**

    Args:
        vq_method (str): Velocity calculation method for Muskingum routing subtypes.
        min_velocity, flow_threshold, velocity_constant, velocity_exponent (float): Parameters used when
            ``vq_method == 'VQ POWER LAW'``.
        vq_nrows (int): Number of velocity-flow rating rows used when ``vq_method == 'VQ RATING'``.
        vq_data (pandas.Dataframe): Velocity-flow rating data used when ``vq_method == 'VQ RATING'``. Columns are
            ``'Velocity'`` and ``'Flow'``.

    Raises:
        NotImplementedError: Raised if class is initialised from blank for unsupported river subtypes.

    Returns:
        RIVER: Flood Modeller RIVER Unit class object
    """

    _unit = "RIVER"
    _section_required_columns = (
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
    _musk_xsec_required_columns = (
        "X",
        "Y",
        "Mannings n",
        "Panel",
        "RPL",
        "Marker",
        "Easting",
        "Northing",
    )
    _musk_vpmc_required_columns = (
        "Flow",
        "Wavespeed",
        "Attenuation",
        "Water Level",
    )

    def _create_from_blank(  # noqa: PLR0913
        self,
        name="new_section",
        subtype="SECTION",
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
        if subtype == "SECTION":
            for param, val in {
                "name": name,
                "comment": comment,
                "subtype": subtype,
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
                if param == "subtype":
                    self._subtype = val
                else:
                    setattr(self, param, val)

            self._data = self._enforce_dataframe(data, self._section_required_columns)
            self._active_data = None

        else:
            # This block is triggered for River subtypes which aren't yet supported
            msg = f"This River sub-type: '{subtype}' is currently unsupported for reading/editing"
            raise NotImplementedError(msg)

    def _read(self, riv_block):
        """Function to read a given RIVER block and store data as class attributes."""

        self._subtype = riv_block[1].split(" ")[0].strip()
        # Extends label line to be correct length before splitting to pick up blank labels
        labels = split_n_char(f"{riv_block[2]:<{7 * self._label_len}}", self._label_len)

        reader = {
            "SECTION": self._read_section,
            "MUSKINGUM": self._read_muskingum,
            "MUSK-XSEC": self._read_musk_xsec,
            "MUSK-VPMC": self._read_musk_vpmc,
            "MUSK-RSEC": self._read_musk_rsec,
        }.get(self.subtype)
        if reader is not None:
            reader(riv_block, labels)
            self._active_data = None
            return

        # This is triggered for river subtypes which aren't yet supported, and just keeps the 'riv_block' in it's raw state to write back.
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

        writer = {
            "SECTION": self._write_section,
            "MUSKINGUM": self._write_muskingum,
            "MUSK-XSEC": self._write_musk_xsec,
            "MUSK-VPMC": self._write_musk_vpmc,
            "MUSK-RSEC": self._write_musk_rsec,
        }.get(self.subtype)
        if writer is not None:
            _validate_unit(self)
            return writer()

        return self._raw_block

    def _write_section(self) -> list[str]:
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

    def _read_section(self, riv_block: list[str], labels: list[str]) -> None:
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
        self._data = pd.DataFrame(data_list, columns=self._section_required_columns)

    def _read_musk_labels(self, riv_block: list[str], labels: list[str]) -> None:
        self.name = labels[0]
        self.first_lateral_inflow_node = labels[1]
        self.second_lateral_inflow_node = labels[2]
        self.lat1 = labels[3]
        self.lat2 = labels[4]
        self.lat3 = labels[5]
        self.lat4 = labels[6]
        self.comment = self._remove_unit_name(riv_block[0])

    def _write_musk_labels(self) -> str:
        return join_n_char_ljust(
            self._label_len,
            self.name,
            self.first_lateral_inflow_node,
            self.second_lateral_inflow_node,
            self.lat1,
            self.lat2,
            self.lat3,
            self.lat4,
        )

    def _read_muskingum(self, riv_block: list[str], labels: list[str]) -> None:
        self.name = labels[0]
        self.comment = self._remove_unit_name(riv_block[0])

        params = split_10_char(f"{riv_block[3]:<20}")
        self.dist_to_next = to_float(params[0])
        self.bed_elevation = to_float(params[1])

        params = split_10_char(f"{riv_block[4]:<20}")
        self.k = to_float(params[0])
        self.x = to_float(params[1])

        self.vq_method = riv_block[5].strip()
        self._read_vq_data(riv_block[6:])

    def _write_muskingum(self) -> list[str]:
        return [
            self._create_header(),
            self.subtype,  # type: ignore
            join_n_char_ljust(self._label_len, self.name),
            join_10_char(self.dist_to_next, self.bed_elevation),
            join_10_char(self.k, self.x),
            *self._write_vq_data(),
        ]

    def _read_musk_xsec(self, riv_block: list[str], labels: list[str]) -> None:
        self._read_musk_labels(riv_block, labels)

        params = split_10_char(f"{riv_block[3]:<70}")
        self.dist_to_next = to_float(params[0])
        self.bed_elevation = to_float(params[1])
        self.slope = to_float(params[2])
        self.min_subnodes = to_int(params[3], 2)
        self.max_subnodes = to_int(params[4], 100)
        self.max_flow = to_float(params[5])
        self.low_flow_smoothing_factor = to_float(params[6])

        self.nrows = to_int(split_10_char(riv_block[5])[0])
        self._data = self._read_musk_xsec_data(riv_block[6 : 6 + self.nrows])

        vq_start = 6 + self.nrows
        self.vq_method = riv_block[vq_start].strip()
        self._read_vq_data(riv_block[vq_start + 1 :])

    def _read_musk_xsec_data(self, rows: list[str]) -> pd.DataFrame:
        data_list = []
        for row in rows:
            row_split = split_10_char(f"{row:<70}")
            panel = row_split[3][:1] == "*"
            rpl = to_float(row_split[3][1 if panel else 0 :].strip())
            data_list.append(
                [
                    to_float(row_split[0]),
                    to_float(row_split[1]),
                    to_float(row_split[2]),
                    panel,
                    rpl,
                    row_split[4],
                    to_float(row_split[5]),
                    to_float(row_split[6]),
                ],
            )
        return pd.DataFrame(data_list, columns=self._musk_xsec_required_columns)

    def _write_musk_xsec(self) -> list[str]:
        params = (
            f"{self.dist_to_next:>10.3f}"
            f"{self.bed_elevation:>10.3f}"
            f"{self.slope:>10.8f}"
            f"{self.min_subnodes:>10}"
            f"{self.max_subnodes:>10}"
            f"{join_10_char(self.max_flow)}"
            f"{join_10_char(self.low_flow_smoothing_factor)}"
        )
        self.nrows = len(self._data)
        riv_block = [
            self._create_header(),
            self.subtype,
            self._write_musk_labels(),
            params,
            "CROSS SECTION",
            f"{self.nrows!s:>10}",
        ]
        riv_block.extend(self._write_musk_xsec_data())
        riv_block.extend(self._write_vq_data())
        return riv_block  # type: ignore

    def _write_musk_xsec_data(self) -> list[str]:
        data = self._data.copy()
        data["Panel/RPL"] = [
            f"{'*' if panel else ' '}{rpl:>9.3f}"
            for panel, rpl in zip(data["Panel"], data["RPL"], strict=True)
        ]
        return write_dataframe(
            None,
            data[["X", "Y", "Mannings n", "Panel/RPL", "Marker", "Easting", "Northing"]],
        )

    def _read_musk_vpmc(self, riv_block: list[str], labels: list[str]) -> None:
        self._read_musk_labels(riv_block, labels)

        params = split_10_char(f"{riv_block[3]:<60}")
        self.dist_to_next = to_float(params[0])
        self.bed_elevation = to_float(params[1])
        self.slope = to_float(params[2], 0.0)
        self.min_subnodes = to_int(params[3], 2)
        self.max_subnodes = to_int(params[4], 100)
        self.specified_discharge = to_float(params[5])

        self.nrows = to_int(split_10_char(riv_block[5])[0])
        self.wavespeed_data = self._read_musk_vpmc_data(riv_block[6 : 6 + self.nrows])

        vq_start = 6 + self.nrows
        self.vq_method = riv_block[vq_start].strip()
        self._read_vq_data(riv_block[vq_start + 1 :])

    def _read_musk_vpmc_data(self, rows: list[str]) -> pd.DataFrame:
        data_list = []
        for row in rows:
            row_split = split_10_char(f"{row:<40}")
            data_list.append(
                [
                    to_float(row_split[0]),
                    to_float(row_split[1]),
                    to_float(row_split[2]),
                    to_float(row_split[3]),
                ],
            )
        return pd.DataFrame(data_list, columns=self._musk_vpmc_required_columns)

    def _write_musk_vpmc(self) -> list[str]:
        params = (
            f"{self.dist_to_next:>10.3f}"
            f"{self.bed_elevation:>10.3f}"
            f"{join_10_char(self.slope)}"
            f"{self.min_subnodes:>10}"
            f"{self.max_subnodes:>10}"
            f"{join_10_char(self.specified_discharge)}"
        )
        self.nrows = len(self.wavespeed_data)
        riv_block = [
            self._create_header(),
            self.subtype,
            self._write_musk_labels(),
            params,
            "WAVESPEED ATTENUATION",
            f"{self.nrows!s:>10}",
        ]
        riv_block.extend(self._write_musk_vpmc_data())
        riv_block.extend(self._write_vq_data())
        return riv_block  # type: ignore

    def _write_musk_vpmc_data(self) -> list[str]:
        return [
            join_10_char(flow, wavespeed, attenuation, water_level)
            for _, flow, wavespeed, attenuation, water_level in self.wavespeed_data.itertuples()
        ]

    def _read_musk_rsec(self, riv_block: list[str], labels: list[str]) -> None:
        self._read_musk_labels(riv_block, labels)

        params = split_10_char(f"{riv_block[3]:<20}")
        self.dist_to_next = to_float(params[0])
        self.bed_elevation = to_float(params[1])

        self.roughness_type = riv_block[5].strip()

        params = split_10_char(f"{riv_block[6]:<20}")
        self.channel_roughness = to_float(params[0])
        self.floodplain_roughness = to_float(params[1])

        params = split_10_char(f"{riv_block[7]:<20}")
        self.channel_slope = to_float(params[0])
        self.floodplain_slope = to_float(params[1])

        params = split_10_char(f"{riv_block[8]:<40}")
        self.b1 = to_float(params[0])
        self.b2 = to_float(params[1])
        self.b3 = to_float(params[2])
        self.b4 = to_float(params[3])

        params = split_10_char(f"{riv_block[9]:<40}")
        self.d1 = to_float(params[0])
        self.d2 = to_float(params[1])
        self.d3 = to_float(params[2])
        self.d4 = to_float(params[3])

        self.vs = to_float(split_10_char(f"{riv_block[10]:<10}")[0])

        params = split_10_char(f"{riv_block[11]:<20}")
        self.max_flow = to_float(params[0])
        self.bankfull_proportion = to_float(params[1])

        self.vq_method = riv_block[12].strip()
        self._read_vq_data(riv_block[13:])

    def _write_musk_rsec(self) -> list[str]:
        return [
            self._create_header(),
            self.subtype,  # type: ignore
            self._write_musk_labels(),
            join_10_char(self.dist_to_next, self.bed_elevation),
            "RIBAMAN",
            self.roughness_type,
            f"{self.channel_roughness:>10.5f}{self.floodplain_roughness:>10.5f}",
            f"{self.channel_slope:>10.8f}{self.floodplain_slope:>10.8f}",
            join_10_char(self.b1, self.b2, self.b3, self.b4),
            join_10_char(self.d1, self.d2, self.d3, self.d4),
            join_10_char(self.vs),
            join_10_char(self.max_flow, self.bankfull_proportion),
            *self._write_vq_data(),
        ]

    def _read_vq_data(self, vq_block: list[str]) -> None:
        if self.vq_method == "VQ SECTION":
            return

        if self.vq_method == "VQ POWER LAW":
            params = split_10_char(f"{vq_block[0]:<40}")
            self.min_velocity = to_float(params[0])
            self.flow_threshold = to_float(params[1])
            self.velocity_constant = to_float(params[2])
            self.velocity_exponent = to_float(params[3])
            return

        if self.vq_method == "VQ RATING":
            self.vq_nrows = to_int(split_10_char(vq_block[0])[0])
            data_list = []
            for row in vq_block[1 : 1 + self.vq_nrows]:
                row_split = split_10_char(f"{row:<20}")
                data_list.append([to_float(row_split[0]), to_float(row_split[1])])
            self.vq_data = pd.DataFrame(data_list, columns=["Velocity", "Flow"])
            return

        msg = f"Unsupported {self.subtype} velocity method: {self.vq_method}"
        raise NotImplementedError(msg)

    def _write_vq_data(self) -> list[str]:
        if self.vq_method == "VQ SECTION":
            return [self.vq_method]

        if self.vq_method == "VQ POWER LAW":
            return [
                self.vq_method,
                join_10_char(
                    self.min_velocity,
                    self.flow_threshold,
                    self.velocity_constant,
                    self.velocity_exponent,
                ),
            ]

        if self.vq_method == "VQ RATING":
            self.vq_nrows = len(self.vq_data)
            return [self.vq_method, *write_dataframe(f"{self.vq_nrows!s:>10}", self.vq_data)]

        msg = f"Unsupported {self.subtype} velocity method: {self.vq_method}"
        raise NotImplementedError(msg)

    @property
    def location(self) -> tuple[float, float] | None:
        # for RIVER units, source priority is as follows:
        # 1. GXY location if defined
        # 2. BED marker location if not (0,0)
        # 3. Y-min location if not (0,0)
        # 4. None
        if self._location is not None:
            return self._location

        if self.subtype == "SECTION":
            return self._cross_section_location(self.active_data)

        if self.subtype == "MUSK-XSEC":
            return self._cross_section_location(self._data)

        return None

    @location.setter
    def location(self, new_value: tuple[float, float] | None) -> None:
        msg = "Currently unit location is read-only."
        raise NotImplementedError(msg)

    def _cross_section_location(self, data: pd.DataFrame) -> tuple[float, float] | None:
        try:
            bed_rows = data["Marker"].str.upper() == "BED"
            bed_points = data.loc[bed_rows]
            first_bed = bed_points[["Easting", "Northing"]].iloc[0]
            location = (float(first_bed["Easting"]), float(first_bed["Northing"]))
            if location != (0, 0):
                return location
        except (AttributeError, ValueError, IndexError):
            logging.debug(
                "Unable to derive RIVER location from BED marker; falling back to Y-min row.",
                exc_info=True,
            )

        try:
            min_idx = data.Y.idxmin()
            min_row = data.loc[min_idx]
            location = (float(min_row["Easting"]), float(min_row["Northing"]))
            if location != (0, 0):
                return location
        except (AttributeError, ValueError, IndexError):
            logging.debug(
                "Unable to derive RIVER location from Y-min row; returning None.",
                exc_info=True,
            )

        return None

    @property
    def data(self) -> pd.DataFrame:
        """Data table for the river cross section.

        Returns:
            pd.DataFrame: Pandas dataframe for the cross section data with columns: 'X', 'Y',
            'Mannings n', 'Panel', 'RPL', 'Marker', 'Easting', 'Northing', 'Deactivation',
            'SP. Marker'
        """
        if self.subtype not in {"SECTION", "MUSK-XSEC"}:
            msg = (
                f"data is only available for RIVER SECTION and MUSK-XSEC units, not {self.subtype}."
            )
            raise NotImplementedError(msg)

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
        if self.subtype not in {"SECTION", "MUSK-XSEC"}:
            msg = (
                f"data is only available for RIVER SECTION and MUSK-XSEC units, not {self.subtype}."
            )
            raise NotImplementedError(msg)

        if not isinstance(new_df, pd.DataFrame):
            msg = "The updated data table for a cross section must be a pandas DataFrame."
            raise ValueError(msg)
        required_columns = (
            self._musk_xsec_required_columns
            if self.subtype == "MUSK-XSEC"
            else self._section_required_columns
        )
        if list(map(str.lower, new_df.columns)) != list(map(str.lower, required_columns)):
            msg = f"The DataFrame must only contain columns: {required_columns}"
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
        if self.subtype != "SECTION":
            msg = f"active_data is only available for RIVER SECTION units, not {self.subtype}."
            raise NotImplementedError(msg)

        if self._active_data is not None:
            return self._active_data
        left_bank_idx, right_bank_idx = self._get_left_right_active_index()
        self._active_data = self._data.iloc[left_bank_idx : right_bank_idx + 1].copy()
        return self._active_data

    @active_data.setter
    def active_data(self, new_df: pd.DataFrame) -> None:
        if self.subtype != "SECTION":
            msg = f"active_data is only available for RIVER SECTION units, not {self.subtype}."
            raise NotImplementedError(msg)

        if not isinstance(new_df, pd.DataFrame):
            msg = "The updated data table for a cross section must be a pandas DataFrame."
            raise ValueError(msg)
        if new_df.columns.to_list() != self._section_required_columns:
            msg = f"The DataFrame must only contain columns: {self._section_required_columns}"
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
