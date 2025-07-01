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
    get_int,
    join_10_char,
    join_n_char_ljust,
    read_bridge_cross_sections,
    read_bridge_culvert_data,
    read_bridge_opening_data,
    read_bridge_pier_locations,
    read_dataframe_from_lines,
    read_spill_section_data,
    read_superbridge_block_data,
    read_superbridge_opening_data,
    set_bridge_params,
    set_pier_params,
    split_10_char,
    split_n_char,
    to_float,
    to_int,
    to_str,
    write_dataframe,
    write_dataframes,
)


class BRIDGE(Unit):
    """Class to hold and process BRIDGE unit type. The Bridge class supports the three main bridge sub-types in
    Flood Modeller: Arch, USBPR1978 and Pierloss. Each of these sub-types forms a unique instance of the class
    which is differentiated by the `BRIDGE.subtype` attribute. All bridge types have the same common attributes:

    **Common Attributes**

    Args:
        name (str): Bridge section name
        comment (str): Comment included in unit
        ds_label (str): Downstream label
        us_remote_label, ds_remote_label (str): Remote labels
        subtype (str): Defines the type of bridge unit (*Should not be changed*)

    **ARCH Type (``BRIDGE.subtype == 'ARCH'``)**

    Args:
        calibration_coefficient (float): Calibration coefficient
        skew (float): Bridge skew
        bridge_width_dual (float): If modelled as dual bridge, the distance between upstream and downstream face of
            bridge (0.00 if not modelling as dual bridge):
        bridge_dist_dual (float): If modelled as dual bridge, the total distance between upstream and downstream
            faces of both bridges (0.00 if not modelling as dual bridge):
        orifice_flow (bool): Whether or not to model surcharged bridge as orifice flow
        orifice_lower_transition_dist, orifice_upper_transition_dist (float): Upper and lower transition distances
            for when using orifice flow
        orifice_discharge_coefficient (float): Orifice discharge coefficient for when using orifice flow
        section_data (pandas.DataFrame): Dataframe object representing the cross section. Columns are ``'X'``, ``'Y'``,
            ``'Mannings n'`` and ``'Embankments'``
        opening_data (pandas.DataFrame): Dataframe object representing the openings in the bridge. Columns are
            ``'Start'``, ``'Finish'``, ``'Springing Level'`` and ``'Soffit Level'``

    **USBPR Type (``BRIDGE.subtype == 'USBPR1978'``)**

    Args:
        calibration_coefficient (float): Calibration coefficient
        skew (float): Bridge skew
        bridge_width_dual (float): If modelled as dual bridge, the distance between upstream and downstream face of bridge
            (0.00 if not modelling as dual bridge)
        bridge_dist_dual (float): If modelled as dual bridge, the total distance between upstream and downstream faces of
            both bridges (0.00 if not modelling as dual bridge)
        orifice_flow (bool): Whether or not to model surcharged bridge as orifice flow
        orifice_lower_transition_dist, orifice_upper_transition_dist (float): Transition distances for when using orifice flow
        orifice_discharge_coefficient (float): Orifice discharge coefficient for when using orifice flow
        abutment_type (str): Type of abutment: ``'3'`` (default), ``'2'`` (30-degree wing wall abutment), ``'1'`` (span between
            abutments < 60 metres and either 90-degree wing or vertical wall abutment)
        abutment_alignment (str): Abutment alignment to normal direction of flow: ``'ALIGNED'`` or ``'SKEW'``
        specify_piers (bool): Whether or not to explicity model piers
        total_pier_width (float): Total width of all piers at right ange to flow direction, only used if ``specify_piers == True``
        npiers (int): Total number of piers in direction of flow, only used if ``specify_piers == True``
        pier_use_calibration_coeff (bool): Whether to use a calibration coefficient to model piers. If set to False it would use
            the pier shape.
        pier_calibration_coeff (float): Calibration coefficient for modelling piers, only used if
            ``specify_piers == True AND pier_use_calibration_coeff == True``
        pier_shape (str): Cross-sectional pier shape with options: ``'RECTANGLE'``, ``'CYLINDER'``, ``'SQUARE'``, ``'I-BEAM'``.
            Only used if ``specify_piers == True AND pier_use_calibration_coeff == False``
        pier_faces (str): Shape of pier faces with options: ``'STREAMLINE'``, ``'SEMICIRCLE'``, ``'TRIANGLE'``, ``'DIAPHRAGM'``.
            Only used if ``specify_piers == True AND pier_use_calibration_coeff == False``
        soffit_shape (str): Shape of soffit (``'FLAT'`` or ``'ARCH'``), only used if ``specify_piers == False``
        section_data (pandas.Dataframe): Dataframe object representing the cross section. Columns are ``'X'``, ``'Y'``, ``'Mannings n'``
            and ``'Embankments'``
        opening_data (pandas.Dataframe): Dataframe object representing the openings in the bridge. Columns are ``'Start'``, ``'Finish'``,
            ``'Springing Level'`` and ``'Soffit Level'``
        culvert_data (pandas.Dataframe): Dataframe object representing any flood relief culverts in the bridge. Columns are ``'Invert'``,
            ``'Soffit'``, ``'Section Area'``, ``'Cd Part Full'``, ``'Cd Full'`` and ``'Drowning Coefficient'``

    **PIERLOSS Type (``BRIDGE.subtype == 'PIERLOSS'``)**

    Args:
        calibration_coefficient (float): Calibration coefficient
        orifice_flow (bool): Whether or not to model surcharged bridge as orifice flow
        orifice_lower_transition_dist, orifice_upper_transition_dist (float): Transition distances for when using orifice flow
        orifice_discharge_coefficient (float): Orifice discharge coefficient for when using orifice flow
        pier_coefficient (float): Pier coefficient
        bridge_width (float): Distance in direction of flow from U/S to D/S cross section of bridge (for reference only)
        us_section_data (pandas.Dataframe): Dataframe object representing the upstream cross section. Columns are ``'X'``, ``'Y'``,
            ``'Mannings n'``, ``'Embankments'`` and ``'Top Level'``
        ds_section_data (pandas.Dataframe): Dataframe object representing the downstream cross section, if no downstream section is
            specified this will be an empty dataframe. Columns are ``'X'``, ``'Y'``, ``'Mannings n'``, ``'Embankments'`` and ``'Top Level'``
        pier_locs_data (pandas.Dataframe): Dataframe object representing the pier locations. Columns are ``'Left X'``, ``'Left Top Level'``,
            ``'Right X'``, ``'Right Top Level'``


    Raises:
        NotImplementedError: Raised if class is initialised without existing Bridge block (i.e. if attempting to create new Bridge unit).
            This will be an option for future releases

    Returns:
        BRIDGE: Flood Modeller BRIDGE Unit class object
    """

    _unit = "BRIDGE"

    # attributes set in a function (for mypy)
    calibration_coefficient: float
    skew: float
    bridge_width_dual: float
    bridge_dist_dual: float
    total_pier_width: float
    orifice_flow: bool
    orifice_lower_transition_dist: float
    orifice_upper_transition_dist: float
    orifice_discharge_coefficient: float
    specify_piers: bool
    npiers: int
    pier_use_calibration_coeff: bool
    pier_calibration_coeff: float
    pier_shape: str
    soffit_shape: str
    pier_faces: str

    def _read(self, br_block: list[str]) -> None:  # noqa: PLR0915
        """Function to read a given BRIDGE block and store data as class attributes"""
        self.comment = self._remove_unit_name(br_block[0])
        self._subtype = self._get_first_word(br_block[1])
        # Extends label line to be correct length before splitting to pick up blank labels
        labels = split_n_char(f"{br_block[2]:<{4*self._label_len}}", self._label_len)
        self.name = labels[0]
        self.ds_label = labels[1]
        self.us_remote_label = labels[2]
        self.ds_remote_label = labels[3]

        # Read ARCH type unit
        if self.subtype == "ARCH":
            set_bridge_params(self, br_block[4], include_pier=False)

            self.section_nrows, end_idx, self.section_data = read_dataframe_from_lines(
                br_block,
                5,
                read_bridge_cross_sections,
            )

            self.opening_nrows, end_idx, self.opening_data = read_dataframe_from_lines(
                br_block,
                end_idx,
                read_bridge_opening_data,
            )

        # Read USBPR type unit
        elif self.subtype == "USBPR1978":
            set_bridge_params(self, br_block[4])

            self.abutment_type = split_10_char(br_block[5])[0]
            self.abutment_alignment = split_10_char(br_block[7])[0]

            set_pier_params(self, br_block[6])

            self.section_nrows, end_idx, self.section_data = read_dataframe_from_lines(
                br_block,
                8,
                read_bridge_cross_sections,
            )

            self.opening_nrows, end_idx, self.opening_data = read_dataframe_from_lines(
                br_block,
                end_idx,
                read_bridge_opening_data,
            )

            self.culvert_nrows, end_idx, self.culvert_data = read_dataframe_from_lines(
                br_block,
                end_idx,
                read_bridge_culvert_data,
            )

        # Read Pierloss type bridge
        elif self.subtype == "PIERLOSS":
            # Read Params
            pierloss_params = split_10_char(f"{br_block[4]:<50}")
            self.calibration_coefficient = to_float(pierloss_params[0], 1.0)
            self.orifice_flow = pierloss_params[1] == "ORIFICE"
            self.orifice_discharge_coefficient = to_float(pierloss_params[2], 1.0)
            self.orifice_lower_transition_dist = to_float(pierloss_params[3])
            self.orifice_upper_transition_dist = to_float(pierloss_params[4])

            additional_params = split_10_char(f"{br_block[5]:<20}")
            self.pier_coefficient = to_float(additional_params[0], 0.9)
            self.bridge_width = to_float(additional_params[1])

            self.us_section_nrows, end_idx, self.us_section_data = read_dataframe_from_lines(
                br_block,
                6,
                read_bridge_cross_sections,
                include_top_level=True,
            )

            self.ds_section_nrows, end_idx, self.ds_section_data = read_dataframe_from_lines(
                br_block,
                end_idx,
                read_bridge_cross_sections,
                include_top_level=True,
            )

            self.pier_locs_nrows, end_idx, self.pier_locs_data = read_dataframe_from_lines(
                br_block,
                end_idx,
                read_bridge_pier_locations,
            )

        elif self.subtype == "INTEGRATED":
            self.revision = to_int(br_block[3])
            self.bridge_name = br_block[4]
            self.integrated_subtype = br_block[5].strip()
            set_bridge_params(self, br_block[6])
            self.abutment_type = to_int(br_block[7])
            set_pier_params(self, br_block[8])
            self.aligned = br_block[9].strip() == "ALIGNED"

            end_idx = 10
            self.section_nrows_list: list[int] = []
            self.section_data_list: list[pd.DataFrame] = []
            for _ in range(4):
                nrows, end_idx, data = read_dataframe_from_lines(
                    br_block,
                    end_idx,
                    read_bridge_cross_sections,
                    include_panel_marker=True,
                )
                self.section_nrows_list.append(nrows)
                self.section_data_list.append(data)

            self.opening_type = br_block[end_idx]
            end_idx += 1
            self.opening_nrows = get_int(br_block[end_idx])
            end_idx += 1
            self.opening_nsubrows_list: list[int] = []
            self.opening_data_list: list[pd.DataFrame] = []
            for _ in range(self.opening_nrows):
                nrows, end_idx, data = read_dataframe_from_lines(
                    br_block,
                    end_idx,
                    read_superbridge_opening_data,
                )
                self.opening_nsubrows_list.append(nrows)
                self.opening_data_list.append(data)

            self.culvert_nrows, end_idx, self.culvert_data = read_dataframe_from_lines(
                br_block,
                end_idx,
                read_bridge_culvert_data,
            )

            spill_params = split_10_char(f"{br_block[end_idx]:<30}")
            self.weir_coefficient = to_float(spill_params[1])
            self.modular_limit = to_float(spill_params[2])
            self.spill_nrows, end_idx, self.spill_data = read_dataframe_from_lines(
                br_block,
                end_idx,
                read_spill_section_data,
            )

            self.block_comment = br_block[end_idx]
            end_idx += 1
            block_params = split_10_char(f"{br_block[end_idx]:<50}")
            self.inlet_loss = to_float(block_params[1])
            self.outlet_loss = to_float(block_params[2])
            self.block_method = "USDEPTH" if (block_params[3] == "") else block_params[3]
            self.override = block_params[4] == "OVERRIDE"
            self.block_nrows, end_idx, self.block_data = read_dataframe_from_lines(
                br_block,
                end_idx,
                read_superbridge_block_data,
            )

        else:
            # This else block is triggered for bridge subtypes which aren't yet supported
            # and just keeps the 'br_block' in its raw state to write back.
            logging.warning(
                "This Bridge sub-type: '%s' is currently unsupported for reading/editing",
                self.subtype,
            )
            self._raw_block = br_block
            self.name = br_block[2][:12].strip()

    def _write(self) -> list[str]:  # noqa: PLR0915
        """Function to write a valid BRIDGE block"""
        _validate_unit(self)  # Function to check the params are valid for BRIDGE unit
        header = self._create_header()
        labels = join_n_char_ljust(
            self._label_len,
            self.name,
            self.ds_label,
            self.us_remote_label,
            self.ds_remote_label,
        )
        br_block = [header, self.subtype, labels]

        if self.subtype == "ARCH":
            orifice = "ORIFICE" if self.orifice_flow else ""
            params = join_10_char(
                self.calibration_coefficient,
                self.skew,
                self.bridge_width_dual,
                self.bridge_dist_dual,
                "",
                orifice,
                self.orifice_lower_transition_dist,
                self.orifice_upper_transition_dist,
                self.orifice_discharge_coefficient,
            )
            br_block.extend(["MANNING", params])

            self.section_nrows = len(self.section_data)
            section_data = write_dataframe(self.section_nrows, self.section_data, empty=3)
            br_block.extend(section_data)

            self.opening_nrows = len(self.opening_data)
            opening_data = write_dataframe(self.opening_nrows, self.opening_data)
            br_block.extend(opening_data)

            return br_block

        if self.subtype == "USBPR1978":
            orifice = "ORIFICE" if self.orifice_flow else ""
            params = join_10_char(
                self.calibration_coefficient,
                self.skew,
                self.bridge_width_dual,
                self.bridge_dist_dual,
                self.total_pier_width,
                orifice,
                self.orifice_lower_transition_dist,
                self.orifice_upper_transition_dist,
                self.orifice_discharge_coefficient,
            )
            if self.specify_piers:
                if self.pier_use_calibration_coeff:
                    pier_params = f'{self.npiers:>10}{"COEFF":<10}{"":>10}{self.pier_calibration_coeff:>10.3f}'
                else:
                    pier_params = f"{self.npiers:>10}{self.pier_shape:<10}{self.pier_faces:<10}"
            else:
                pier_params = f"{0:>10}{self.soffit_shape}"

            br_block.extend(
                [
                    "MANNING",
                    params,
                    f"{self.abutment_type!s:>10}",
                    pier_params,
                    self.abutment_alignment,
                ],
            )

            self.section_nrows = len(self.section_data)
            section_data = write_dataframe(self.section_nrows, self.section_data, empty=3)
            br_block.extend(section_data)

            self.opening_nrows = len(self.opening_data)
            opening_data = write_dataframe(self.opening_nrows, self.opening_data)
            br_block.extend(opening_data)

            self.culvert_nrows = len(self.culvert_data)
            culvert_data = write_dataframe(self.culvert_nrows, self.culvert_data)
            br_block.extend(culvert_data)

            return br_block

        if self.subtype == "PIERLOSS":
            orifice = "ORIFICE" if self.orifice_flow else ""
            params = join_10_char(
                self.calibration_coefficient,
                orifice,
                self.orifice_discharge_coefficient,
                self.orifice_lower_transition_dist,
                self.orifice_upper_transition_dist,
            )
            additional_params = join_10_char(self.pier_coefficient, self.bridge_width)
            br_block.extend(["YARNELL", params, additional_params])

            self.us_section_nrows = len(self.us_section_data)
            us_section_data = write_dataframe(self.us_section_nrows, self.us_section_data, empty=3)
            br_block.extend(us_section_data)

            self.ds_section_nrows = len(self.ds_section_data)
            ds_section_data = write_dataframe(self.ds_section_nrows, self.ds_section_data, empty=3)
            br_block.extend(ds_section_data)

            self.pier_locs_nrows = len(self.pier_locs_data)
            pier_locs_data = write_dataframe(self.pier_locs_nrows, self.pier_locs_data)
            br_block.extend(pier_locs_data)

            return br_block

        if self.subtype == "INTEGRATED":
            line_1_2 = br_block
            line_3 = str(self.revision)
            line_4 = self.bridge_name
            line_5 = self.integrated_subtype
            line_6 = join_10_char(
                self.calibration_coefficient,
                self.skew,
                self.bridge_width_dual,
                self.bridge_dist_dual,
                self.total_pier_width,
                "ORIFICE" if self.orifice_flow else "",
                self.orifice_lower_transition_dist,
                self.orifice_upper_transition_dist,
                self.orifice_discharge_coefficient,
            )
            line_7 = str(self.abutment_type)
            if self.specify_piers:
                if self.pier_use_calibration_coeff:
                    line_8 = join_10_char(
                        self.npiers,
                        "COEFF",
                        "",
                        self.pier_calibration_coeff,
                    )
                else:
                    line_8 = join_10_char(
                        self.npiers,
                        self.pier_shape,
                        self.pier_faces,
                    )
            else:
                line_8 = join_10_char(
                    0,
                    self.soffit_shape,
                )
            line_9 = "ALIGNED" if self.aligned else ""
            line_10_11_12_13 = write_dataframes(
                None,
                self.section_nrows_list,
                self.section_data_list,
            )
            line_14 = self.opening_type
            line_15 = write_dataframes(
                self.opening_nrows,
                self.opening_nsubrows_list,
                self.opening_data_list,
            )
            line_16 = write_dataframe(self.culvert_nrows, self.culvert_data)
            line_17 = write_dataframe(
                join_10_char(self.spill_nrows, self.weir_coefficient, self.modular_limit),
                self.spill_data,
            )
            line_18 = self.block_comment
            line_19 = write_dataframe(
                join_10_char(
                    self.block_nrows,
                    self.inlet_loss,
                    self.outlet_loss,
                    self.block_method,
                    "OVERRIDE" if self.override else "NOOVERRIDE",
                ),
                self.block_data,
            )

            return [
                *line_1_2,
                line_3,
                line_4,
                line_5,  # type: ignore
                line_6,
                line_7,
                line_8,
                line_9,
                *line_10_11_12_13,
                line_14,
                *line_15,
                *line_16,
                *line_17,
                line_18,
                *line_19,
            ]

        return self._raw_block


class SLUICE(Unit):
    """The Sluice class supports two sluice sub-types in Flood Modeller: RADIAL and VERTICAL. Each of these sub-types forms
    a unique instance of the class which is differentiated by the `SLUICE.subtype` attribute. There are also several different
    attributes depending on the `.control_method` used. All sluice types have the same common attributes:

    **Common Attributes**

    Args:
        name (str): Sluice section name (upstream label)
        ds_label (str): Downstream label
        remote_label (str): Remote label
        comment (str): Comment included in unit
        subtype (str): Defines the type of sluice unit (*Should not be changed*)
        weir_flow_coefficient (float): Coefficient of approach velocity for weir flow (0.4 - 3.0)
        under_gate_flow (float): Coefficient of approach velocity for under gate flow
        over_gate_flow (float): Coefficient of approach velocity for over gate flow
        weir_breadth (float): breadth of weir (for single gate) perpendicular to flow direction
        crest_elevation (float): Elevation of weir crest
        gate_height_or_chord (float): Height of sluice gate (m) (if sluice subtype is VERTICAL or subtype is RADIAL and
            ``use_degrees == False``). OR the cord made by the arc of sluice gate (m) if subtype is RADIAL and
            ``use_degrees == True``.
        weir_length (float): Length of weir (m) in flow direction
        us_weir_height (float): Vertical distance from weir crest to upstream bed level
        ds_weir_height (float): Vertical distance from weir crest to downstream bed level
        bias_factor (float): Only used when control_method set to 'REMOTE WATER LEVEL'
        modular_limits (dict): Dictionary of modular limit values. Keys: {'weir_flow', 'under_gate_flow', 'over_gate_flow'}. If they
            are all set equal to zero, then a variable calculation method is used.
        ngates (int): number of gates
        timeunit (str): Unit of time, e.g. 'HOURS', 'MINUTES' or 'SECONDS'. See Flood Modeller documentation for all available options.
        extendmethod (str): Data extending method: 'EXTEND', 'NOEXTEND' or 'REPEAT'.


    **Attributes used when ``SLUICE.control_method == 'TIME'``**

    Args:
        gates (List[pandas.Series]): List of Data series representing the gate control with 'Time' index and 'Gate Opening' (m) as the data


    **Attributes used when ``SLUICE.control_method == 'LOGICAL'``**

    Args:
        gates (List[pandas.DataFrame]): List of Dataframes representing the gate control with 'Time' as index and 'Mode' and 'Gate Opening' (m) as the columns.
            The Mode is set to 'AUTO', 'MANUAL' or [blank] depending on the control mode at that time.
        max_movement_rate (float): Maximum movement rate of the structure
        max_setting (float): Maximum setting of the structure
        min_setting (float): Minimum setting of the structure
        rules (List[dict]): List of logical rules to use. Each rule is represented as a Dictionary with keys 'name' and 'logic'.
        time_rule_data (pandas.Series): Series containing data on which operating rules to apply, with index of 'Time' and
            dataseries for 'Operating Rules'
        varrules (List[dict]): List of logical variable rules to use. Each varrule is represented as a Dictionary with keys 'name' and 'logic'.
        time_varrule_data (pandas.Series): Series containing data on which operating rules to apply, with index of 'Time' and
            dataseries for 'Operating Rules'


    **Radial Type (``SLUICE.subtype == 'RADIAL'``)**

    Args:
        use_degrees (bool): Whether to measure gate movement in degrees
        allow_free_flow_under (bool): Whether to allow free flow under gate
        pivot_height (float): Height of gate pivot (m) above sill
        gate_radius (float): Distance from gate pivot to surface (m)

    Returns:
        SLUICE: Flood Modeller SLUICE Unit class object
    """

    _unit = "SLUICE"

    def _read(self, block):
        """Function to read a given SLUICE block and store data as class attributes"""
        self._subtype = self._get_first_word(block[1])

        # Extends label line to be correct length before splitting to pick up blank labels
        labels = split_n_char(f"{block[2]:<{3*self._label_len}}", self._label_len)
        self.name = labels[0]
        self.ds_label = labels[1]
        self.remote_label = labels[2]
        self.comment = self._remove_unit_name(block[0])

        # First parameter line
        params1 = split_10_char(f"{block[3]:<80}")
        self.weir_flow_coefficient = to_float(params1[0], 1.0)
        self.under_gate_flow = to_float(params1[1], 1.0)
        self.weir_breadth = to_float(params1[2])
        self.crest_elevation = to_float(params1[3])
        self.gate_height_or_chord = to_float(params1[4])
        self.weir_length = to_float(params1[5])
        if self.subtype == "RADIAL":
            self.use_degrees = params1[6] == "DEGREES"
            self.allow_free_flow_under = params1[7] == "FREESLUICE"

        # Second parameter line
        params2 = split_10_char(f"{block[4]:<70}")
        self.us_weir_height = to_float(params2[0])
        self.ds_weir_height = to_float(params2[1])
        self.bias_factor = to_float(params2[2], 1.0)
        self.over_gate_flow = to_float(params2[3], 1.0)
        if self.subtype == "RADIAL":
            self.pivot_height = to_float(params2[4], 0.7)
            self.gate_radius = to_float(params2[5], 0.7)
        else:
            self.modular_limits = {
                "weir_flow": to_float(params2[4]),
                "under_gate_flow": to_float(params2[5], 1.0),
                "over_gate_flow": to_float(params2[6], 1.0),
            }

        # Third parameter line
        params3 = split_10_char(f"{block[5]:<60}")
        self.ngates = int(params3[0])  # number of gates
        if self.subtype == "RADIAL":
            self.modular_limits = {
                "weir_flow": to_float(params3[1]),
                "under_gate_flow": to_float(params3[2], 1.0),
                "over_gate_flow": to_float(params3[3], 1.0),
            }
            self.timeunit = to_str(params3[4], "SECONDS", check_float=True)
            self.extendmethod = to_str(params3[5], "EXTEND")
        else:
            self.timeunit = to_str(params3[1], "SECONDS", check_float=True)
            self.extendmethod = to_str(params3[2], "EXTEND")

        # Control lines
        self.control_method = block[6].split()[0].upper()
        if self.control_method == "TIME":
            self.gates = self._get_gates(self.ngates, block, gate_row=7)

        elif self.control_method == "LOGICAL":
            logical_params = split_10_char(block[6])
            self.max_movement_rate = logical_params[1]
            self.max_setting = logical_params[2]
            self.min_setting = logical_params[3]
            self.gates = self._get_gates(self.ngates, block, gate_row=7)
            self._read_rules(block)

        else:
            self._raw_extra_lines = block[6:]
            logging.warning(
                "Note: Sluice control using method: '%s' is not currently supported.",
                self.control_method,
            )

    def _write(self):
        """Function to write a valid SLUICE block"""
        _validate_unit(self)  # Function to check the params are valid for CONDUIT unit
        header = self._create_header()
        labels = join_n_char_ljust(self._label_len, self.name, self.ds_label, self.remote_label)
        block = [header, self.subtype, labels]

        # First parameter line
        params1 = join_10_char(
            self.weir_flow_coefficient,
            self.under_gate_flow,
            self.weir_breadth,
            self.crest_elevation,
            self.gate_height_or_chord,
            self.weir_length,
        )
        if self.subtype == "RADIAL":
            params1 += f'{"DEGREES":<10}' if self.use_degrees else f'{"":<10}'
            params1 += "FREESLUICE" if self.allow_free_flow_under else f'{"":<10}'

        # Second parameter line
        params2 = join_10_char(
            self.us_weir_height,
            self.ds_weir_height,
            self.bias_factor,
            self.over_gate_flow,
        )

        if self.subtype == "RADIAL":
            params2 += join_10_char(self.pivot_height, self.gate_radius)
        else:
            params2 += join_10_char(
                self.modular_limits["weir_flow"],
                self.modular_limits["under_gate_flow"],
                self.modular_limits["over_gate_flow"],
            )

        # Third parameter line
        self.ngates = len(self.gates) if hasattr(self, "gates") else self.ngates
        params3 = join_10_char(self.ngates)

        if self.subtype == "RADIAL":
            params3 += join_10_char(
                self.modular_limits["weir_flow"],
                self.modular_limits["under_gate_flow"],
                self.modular_limits["over_gate_flow"],
            )

        params3 += join_n_char_ljust(10, self.timeunit, self.extendmethod)

        block.extend([params1, params2, params3])

        # Control lines
        if self.control_method == "TIME":
            block.append("TIME")
            n = 1
            for gate in self.gates:
                block.append(f"GATE {n}")
                nrows = len(gate)
                block.append(f"{nrows:>10}")
                gate_data = [f"{join_10_char(t, o)}" for t, o in gate.items()]
                block.extend(gate_data)
                n += 1

        elif self.control_method == "LOGICAL":
            # ADD GATES
            block.append(
                join_10_char(
                    f'{"LOGICAL":<10}',
                    self.max_movement_rate,
                    self.max_setting,
                    self.min_setting,
                ),
            )
            n = 1
            for gate in self.gates:
                block.append(f"GATE {n}")
                nrows = len(gate)
                block.append(f"{nrows:>10}")
                gate_data = [f"{join_10_char(t, m, o)}" for t, m, o in gate.itertuples()]
                block.extend(gate_data)
                n += 1
            block = self._write_rules(block)

        else:
            block.extend(self._raw_extra_lines)

        return block

    def _get_gates(self, ngates, block, gate_row):
        gates = []

        if self.control_method == "TIME":
            for _ in range(ngates):
                nrows = int(split_10_char(block[gate_row + 1])[0])
                data_list = []
                for row in block[gate_row + 2 : gate_row + 2 + nrows]:
                    row_split = split_10_char(f"{row:<20}")
                    x = to_float(row_split[0])  # time
                    y = to_float(row_split[1])  # opening
                    data_list.append([x, y])

                gate_data = pd.DataFrame(data_list, columns=["Time", "Opening"])
                gate_data = gate_data.set_index("Time")
                gate_data = gate_data["Opening"]

                gates.append(gate_data)

                gate_row += 2 + nrows

            self._last_gate_row = gate_row

            return gates

        if self.control_method == "LOGICAL":
            for _ in range(ngates):
                nrows = int(split_10_char(block[gate_row + 1])[0])
                data_list = []
                for row in block[gate_row + 2 : gate_row + 2 + nrows]:
                    row_split = split_10_char(f"{row:<30}")
                    x = to_float(row_split[0])  # time
                    y = row_split[1]  # mode
                    z = to_float(row_split[2])  # opening
                    data_list.append([x, y, z])

                gate_data = pd.DataFrame(data_list, columns=["Time", "Mode", "Opening"])
                gate_data = gate_data.set_index("Time")

                gates.append(gate_data)

                gate_row += 2 + nrows

            self._last_gate_row = gate_row

            return gates
        return None


class ORIFICE(Unit):
    """Class to hold and process ORIFICE unit type

    Args:
        name (str, optional): Unit name.
        comment (str, optional): Comment included in unit.
        flapped (bool, optional): ``True`` if orifice is flapped, ``False`` if orifice is open
        ds_label (str, optional): Downstream label
        invert (float, optional): Throat invert level
        soffit (float, optional): Throat soffit level
        bore_area (float, optional): Cross sectional area of throat opening
        upstream_sill (float, optional): Upstream sill level
        downstream_sill (float, optional): Downstream sill level
        shape (str, optional): Shape of orifice aperture ('RECTANGLE' or 'CIRCULAR')
        weir_flow (float, optional): Calibration factor for weir flow
        surcharged_flow (float, optional): Calibration factor for surcharged flow
        modular_limit (float, optional): Ratio of upstream and downstream heads when switching between free and drowned mode


    Returns:
        ORIFICE: Flood Modeller ORIFICE Unit class object
    """

    _unit = "ORIFICE"

    def _read(self, block):
        """Function to read a given ORIFICE block and store data as class attributes"""
        self._subtype = self._get_first_word(block[1])
        self.flapped = self.subtype == "FLAPPED"

        # Extends label line to be correct length before splitting to pick up blank labels
        labels = split_n_char(f"{block[2]:<{2*self._label_len}}", self._label_len)
        self.name = labels[0]
        self.ds_label = labels[1]
        self.comment = self._remove_unit_name(block[0])

        # First parameter line
        params1 = split_10_char(f"{block[3]:<60}")
        self.invert = to_float(params1[0])
        self.soffit = to_float(params1[1])
        self.bore_area = to_float(params1[2])
        self.upstream_sill = to_float(params1[3])
        self.downstream_sill = to_float(params1[4])
        self.shape = to_str(params1[5], "RECTANGLE")

        # Second parameter line
        params2 = split_10_char(block[4])
        self.weir_flow = to_float(params2[0], 1.0)
        self.surcharged_flow = to_float(params2[1], 1.0)
        self.modular_limit = to_float(params2[2], 0.7)

    def _write(self):
        """Function to write a valid ORIFICE block"""
        _validate_unit(self)  # Function to check the params are valid for CONDUIT unit
        header = self._create_header()
        labels = join_n_char_ljust(self._label_len, self.name, self.ds_label)

        self._subtype = "FLAPPED" if self.flapped else "OPEN"
        block = [header, self.subtype, labels]

        # First parameter line
        params1 = join_10_char(
            self.invert,
            self.soffit,
            self.bore_area,
            self.upstream_sill,
            self.downstream_sill,
            self.shape,
        )

        # Second parameter line
        params2 = join_10_char(self.weir_flow, self.surcharged_flow, self.modular_limit)

        block.extend([params1, params2])

        return block

    def _create_from_blank(  # noqa: PLR0913
        self,
        name="new_orifice",
        flapped=False,
        ds_label="",
        comment="",
        invert=0.0,
        soffit=0.0,
        bore_area=1.0,
        upstream_sill=0.0,
        downstream_sill=0.0,
        shape="RECTANGLE",
        weir_flow=1.0,
        surcharged_flow=1.0,
        modular_limit=0.7,
    ):
        for param, val in {
            "name": name,
            "flapped": flapped,
            "ds_label": ds_label,
            "comment": comment,
            "invert": invert,
            "soffit": soffit,
            "bore_area": bore_area,
            "upstream_sill": upstream_sill,
            "downstream_sill": downstream_sill,
            "shape": shape,
            "weir_flow": weir_flow,
            "surcharged_flow": surcharged_flow,
            "modular_limit": modular_limit,
        }.items():
            setattr(self, param, val)


class SPILL(Unit):
    """Class to hold and process SPILL unit type

    Args:
        name (str, optional): Unit name.
        comment (str, optional): Comment included in unit.
        ds_label (str, optional): Downstream label
        weir_coefficient (float, optional): Weir coefficient
        modular_limit (float, optional): Ratio of upstream and downstream heads when switching between free and drowned mode
        data (pandas.DataFrame): Dataframe object containing all the spill section data.
            Columns are ``'X', 'Y', 'Easting', 'Northing'``

    Returns:
        SPILL: Flood Modeller SPILL Unit class object
    """

    _unit = "SPILL"

    def _read(self, block):
        """Function to read a given SPILL block and store data as class attributes"""
        # Extends label line to be correct length before splitting to pick up blank labels
        labels = split_n_char(f"{block[1]:<{2*self._label_len}}", self._label_len)
        self.name = labels[0]
        self.ds_label = labels[1]
        self.comment = self._remove_unit_name(block[0])

        # First parameter line
        params = split_10_char(block[2])
        self.weir_coefficient = to_float(params[0], 1.2)
        self.modular_limit = to_float(params[1], 0.9)

        # Spill section data
        self.data = read_spill_section_data(block[4:])

    def _write(self):
        """Function to write a valid SPILL block"""
        _validate_unit(self)  # Function to check the params are valid for CONDUIT unit
        header = self._create_header()
        labels = join_n_char_ljust(self._label_len, self.name, self.ds_label)
        block = [header, labels]

        # First parameter line
        params = join_10_char(self.weir_coefficient, self.modular_limit)
        block.append(params)

        # Section data
        nrows = len(self.data)
        block.append(join_10_char(nrows))
        section_data = [join_10_char(x, y, e, n) for _, x, y, e, n in self.data.itertuples()]
        block.extend(section_data)

        return block

    def _create_from_blank(  # noqa: PLR0913
        self,
        name="new_spill",
        ds_label="",
        comment="",
        weir_coefficient=1.2,
        modular_limit=0.9,
        data=None,
    ):
        for param, val in {
            "name": name,
            "ds_label": ds_label,
            "comment": comment,
            "weir_coefficient": weir_coefficient,
            "modular_limit": modular_limit,
        }.items():
            setattr(self, param, val)

        self.data = (
            data
            if isinstance(data, pd.DataFrame)
            else pd.DataFrame([[0.0, 0.0, 0.0, 0.0]], columns=["X", "Y", "Easting", "Northing"])
        )


class RNWEIR(Unit):
    """Class to hold and process RNWEIR unit type

    Args:
        name (str, optional): Upstream label name.
        comment (str, optional): Comment included in unit.
        ds_label (str, optional): Downstream label.
        velocity_coefficient (float, optional): Coefficient of approach velocity.
        weir_length (float, optional): Length of weir crest in the direction of flow (m).
        weir_breadth (float, optional): Breadth of weir at control section (normal to the flow direction)(m).
        weir_elevation (float, optional): Elevation of weir crest (m AD).
        modular_limit (float, optional): Ratio of upstream and downstream heads when switching between free and drowned mode.
        upstream_crest_height (float, optional): Height of crest above bed of upstream channnel (m).
        downstream_crest_height (float, optional): Height of crest above downstream channel (m).

    Returns:
        RNWEIR: Flood Modeller RNWEIR Unit class object"""

    _unit = "RNWEIR"
    ACCEPTABLE_MODULAR_LIMIT = 0.0

    def _read(self, block):
        """Function to read a given RNWEIR block and store data as class attributes"""
        # Extends label line to be correct length before splitting to pick up blank labels
        labels = split_n_char(f"{block[1]:<{2*self._label_len}}", self._label_len)
        self.name = labels[0]
        self.ds_label = labels[1]
        self.comment = self._remove_unit_name(block[0])

        # First parameter line
        params1 = split_10_char(f"{block[2]:<50}")
        self.velocity_coefficient = to_float(params1[0])
        self.weir_length = to_float(params1[1])
        self.weir_breadth = to_float(params1[2])
        self.weir_elevation = to_float(params1[3])
        self.modular_limit = to_float(params1[4])

        # Second parameter line
        params2 = split_10_char(f"{block[3]:<20}")
        self.upstream_crest_height = to_float(params2[0])
        self.downstream_crest_height = to_float(params2[1])

    def _write(self):
        """Function to write a valid RNWEIR block"""
        _validate_unit(self)
        header = self._create_header()
        labels = join_n_char_ljust(self._label_len, self.name, self.ds_label)
        block = [header, labels]

        # First parameter line
        if self.modular_limit == self.ACCEPTABLE_MODULAR_LIMIT:
            params1 = join_10_char(
                self.velocity_coefficient,
                self.weir_length,
                self.weir_breadth,
                self.weir_elevation,
            )
        else:
            params1 = join_10_char(
                self.velocity_coefficient,
                self.weir_length,
                self.weir_breadth,
                self.weir_elevation,
                self.modular_limit,
            )

        block.append(params1)

        # Second parameter line
        params2 = join_10_char(self.upstream_crest_height, self.downstream_crest_height)
        block.append(params2)

        return block

    def _create_from_blank(  # noqa: PLR0913
        self,
        name="new_rnweir",
        comment="",
        ds_label="",
        velocity_coefficient=1.0,
        modular_limit=0.7,
        upstream_crest_height=0.0,
        downstream_crest_height=0.0,
        weir_length=0.0,
        weir_breadth=0.0,
        weir_elevation=0.0,
    ):
        for param, val in {
            "name": name,
            "comment": comment,
            "ds_label": ds_label,
            "velocity_coefficient": velocity_coefficient,
            "modular_limit": modular_limit,
            "upstream_crest_height": upstream_crest_height,
            "downstream_crest_height": downstream_crest_height,
            "weir_length": weir_length,
            "wier_breadth": weir_breadth,
            "weir_elevation": weir_elevation,
        }.items():
            setattr(self, param, val)


class WEIR(Unit):
    """Class to hold and process WEIR unit type

    Args:
        name (str, optional): Upstream label name.
        comment (str, optional): Comment included in unit.
        ds_label (str, optional): Downstream label.
        exponent (float, optional): Coefficient of discharge for the weir,
        discharge_coefficeient (float, optional): Exponent used in the weir flow equation,
        velocity_coefficient (float, optional): Coefficient of approach velocity.
        weir_length (float, optional): Length of weir crest in the direction of flow (m).
        weir_breadth (float, optional): Breadth of weir at control section (normal to the flow direction)(m).
        weir_elevation (float, optional): Elevation of weir crest (m AD).
        modular_limit (float, optional): Ratio of upstream and downstream heads when switching between free and drowned mode.

    Returns:
        WEIR: Flood Modeller WEIR Unit class object"""

    _unit = "WEIR"

    def _read(self, block):
        """Function to read a given WEIR block and store data as class attributes"""
        # Extends label line to be correct length before splitting to pick up blank labels
        labels = split_n_char(f"{block[1]:<{2*self._label_len}}", self._label_len)
        self.name = labels[0]
        self.ds_label = labels[1]
        self.comment = self._remove_unit_name(block[0])

        # Exponent
        self.exponent = to_float(block[2].strip())

        # Parameters line
        params = split_10_char(f"{block[3]:<50}")
        self.discharge_coefficient = to_float(params[0])
        self.velocity_coefficient = to_float(params[1])
        self.weir_breadth = to_float(params[2])
        self.weir_elevation = to_float(params[3])
        self.modular_limit = to_float(params[4])

    def _write(self):
        """Function to write a valid WEIR block"""
        _validate_unit(self)
        header = self._create_header()
        labels = join_n_char_ljust(self._label_len, self.name, self.ds_label)
        block = [header, labels]

        # Exponent line
        exp_line = join_10_char(self.exponent)
        block.append(exp_line)

        # Parameter line
        params = join_10_char(
            self.discharge_coefficient,
            self.velocity_coefficient,
            self.weir_breadth,
            self.weir_elevation,
            self.modular_limit,
        )
        block.append(params)

        return block

    def _create_from_blank(  # noqa: PLR0913
        self,
        name="new_weir",
        comment="",
        ds_label="",
        exponent=1.5,
        discharge_coefficeient=1.0,
        velocity_coefficient=1.0,
        modular_limit=0.7,
        weir_length=0.0,
        weir_breadth=0.0,
        weir_elevation=0.0,
    ):
        for param, val in {
            "name": name,
            "comment": comment,
            "ds_label": ds_label,
            "exponent": exponent,
            "discharge_coefficeient": discharge_coefficeient,
            "velocity_coefficient": velocity_coefficient,
            "modular_limit": modular_limit,
            "weir_length": weir_length,
            "wier_breadth": weir_breadth,
            "weir_elevation": weir_elevation,
        }.items():
            setattr(self, param, val)


class CRUMP(Unit):
    """Class to hold and process CRUMP unit type

    Args:
        name (str, optional): Upstream label name.
        comment (str,optional): Comment included in unit.
        calibration_coefficient (float, optional): Calibration coefficient (should be set to unity for most cases).
        weir_breadth (float, optional): Breadth of weir at crest (m).
        weir_elevation (float, optional): Eleveation of weir crest (m above datum).
        modular_limit (float, optional): Ratio of upstream and downstream heads when switching between free and drowned mode.
        upstream_crest_height (float, optional): Height of crest above bed of upstream channel (m).
        downstream_crest_height (float, optional): Height oof crest above bed of downstream channel (m).
        ds_label (str, optional): Downstream node label.
        us_remote_label (str, optional): Upstream remote node label (must be a river or conduit section) - use if name is not a river or conduit section.
        ds_remote_label (str, optional): Downstream remote node label (must be a river or conduit section) - use if ds_label is not a river or conduit section.

    Returns:
        CRUMP: Flood Modeller CRUMP Unit class object"""

    _unit = "CRUMP"
    ACCEPTABLE_MODULAR_LIMIT = 0.0

    def _read(self, block):
        """Function to read a given CRUMP block and store data as class attributes"""
        # Extends label line to be correct length before splitting to pick up blank labels
        labels = split_n_char(f"{block[1]:<{4*self._label_len}}", self._label_len)
        self.name = labels[0]
        self.ds_label = labels[1]
        self.us_remote_label = labels[2]
        self.ds_remote_label = labels[3]
        self.comment = self._remove_unit_name(block[0])

        # First parameter line
        params1 = split_10_char(f"{block[2]:<40}")
        self.calibration_coefficient = to_float(params1[0])
        self.weir_breadth = to_float(params1[1])
        self.weir_elevation = to_float(params1[2])
        self.modular_limit = to_float(params1[3])

        # Second parameter line
        params2 = split_10_char(f"{block[3]:<20}")
        self.upstream_crest_height = to_float(params2[0])
        self.downstream_crest_height = to_float(params2[1])

    def _write(self):
        """Function to write a valid CRUMP block"""
        _validate_unit(self)
        header = self._create_header()
        labels = join_n_char_ljust(
            self._label_len,
            self.name,
            self.ds_label,
            self.us_remote_label,
            self.ds_remote_label,
        )
        block = [header, labels]

        # First parameter line
        params1 = join_10_char(
            self.calibration_coefficient,
            self.weir_breadth,
            self.weir_elevation,
            self.modular_limit if self.modular_limit != self.ACCEPTABLE_MODULAR_LIMIT else "",
        )

        block.append(params1)

        # Second parameter line
        params2 = join_10_char(self.upstream_crest_height, self.downstream_crest_height)
        block.append(params2)

        return block

    def _create_from_blank(  # noqa: PLR0913
        self,
        name="new_crump",
        comment="",
        calibration_coefficient=1.0,
        weir_breadth=0.0,
        weir_elevation=0.0,
        modular_limit=0.7,
        upstream_crest_height=0.0,
        downstream_crest_height=0.0,
        ds_label="",
        us_remote_label="",
        ds_remote_label="",
    ):
        for param, val in {
            "name": name,
            "comment": comment,
            "calibration_coefficient": calibration_coefficient,
            "weir_breadth": weir_breadth,
            "weir_elevation": weir_elevation,
            "modular_limit": modular_limit,
            "upstream_crest_height": upstream_crest_height,
            "downstream_crest_height": downstream_crest_height,
            "ds_label": ds_label,
            "us_remote_label": us_remote_label,
            "ds_remote_label": ds_remote_label,
        }.items():
            setattr(self, param, val)


class FLAT_V_WEIR(Unit):  # noqa: N801
    """Class to hold and process FLAT-V WEIR unit type

    Args:

    name (str, optional): Upstream label name.
    comment (str,optional): Comment included in unit.
    ds_label (str, optional): Downstream node label.
    us_remote_label (str, optional): Upstream remote node label (must be a river or conduit section) - use if name is not a river or conduit section.
    ds_remote_label (str, optional): Downstream remote node label (must be a river or conduit section) - use if ds_label is not a river or conduit section.
    weir_elevation (float, optional): Eleveation of weir crest (m above datum).
    weir_breadth (float, optional): Breadth of weir at crest (m).
    v_slope (float, optional): 'V' slope (horizontal distance/vertical distance).
    side_slope (float, optional): Channel side slope (horizontal distance/vertical distance).
    upstream_crest_height (float, optional): Weir crest height above upstream bed (m).
    downstream_crest_height (float, optional): Weir crest height above downstream bed (m).
    modular_limit (float, optional): Ratio of upstream and downstream heads when switching between free and drowned mode.
    calibration_coefficient (float, optional): Calibration coefficient (should be set to unity for most cases).
    ds_face_slope (int, optional): Flag to switch between 1:5 or 1:2 for d/s face. Can be set to 2 or 5 ONLY.
    coriolis_coefficient (float, optional): Coriolis energy coefficient.
    bank_top_elevation (float, optional): Elevation of channel bank top/ limit of extent of sloping channel walls (m AD).

    Returns:
        FLAT_V_WEIR: Flood Modeller FLAT-V WEIR Unit class object"""

    _unit = "FLAT-V WEIR"
    ACCEPTABLE_MODULAR_LIMIT = 0.0

    def _read(self, block):
        """Function to read a given FLAT-V WEIR block and store data as class attributes"""
        # Extends label line to be correct length before splitting to pick up blank labels
        labels = split_n_char(f"{block[1]:<{4*self._label_len}}", self._label_len)
        self.name = labels[0]
        self.ds_label = labels[1]
        self.us_remote_label = labels[2]
        self.ds_remote_label = labels[3]
        self.comment = self._remove_unit_name(block[0])

        # First parameter line
        params1 = split_10_char(f"{block[2]:<90}")
        self.calibration_coefficient = to_float(params1[0])
        self.weir_breadth = to_float(params1[1])
        self.weir_elevation = to_float(params1[2])
        self.modular_limit = to_float(params1[3])
        self.v_slope = to_float(params1[4])
        self.side_slope = to_float(params1[5])
        self.ds_face_slope = to_float(params1[6])
        self.coriolis_coefficient = to_float(params1[7])
        self.bank_top_elevation = to_float(params1[8])

        # Second parameter line
        params2 = split_10_char(f"{block[3]:<20}")
        self.upstream_crest_height = to_float(params2[0])
        self.downstream_crest_height = to_float(params2[1])

    def _write(self):
        """Function to write a valid FLAT-V WEIR block"""

        _validate_unit(self)
        header = self._create_header()
        labels = join_n_char_ljust(
            self._label_len,
            self.name,
            self.ds_label,
            self.us_remote_label,
            self.ds_remote_label,
        )
        block = [header, labels]

        params1 = join_10_char(
            self.calibration_coefficient,
            self.weir_breadth,
            self.weir_elevation,
            self.modular_limit if self.modular_limit != self.ACCEPTABLE_MODULAR_LIMIT else "",
            self.v_slope,
            self.side_slope,
            self.ds_face_slope,
            self.coriolis_coefficient,
            self.bank_top_elevation,
        )

        block.append(params1)

        # Second parameter line
        params2 = join_10_char(self.upstream_crest_height, self.downstream_crest_height)
        block.append(params2)

        return block

    def _create_from_blank(  # noqa: PLR0913
        self,
        name="new_flat_v",
        comment="",
        ds_label="",
        us_remote_label="",
        ds_remote_label="",
        weir_elevation=0.0,
        weir_breadth=0.0,
        v_slope=0.0,
        side_slope=0.0,
        upstream_crest_height=0.0,
        downstream_crest_height=0.0,
        modular_limit=0.0,
        calibration_coefficient=1.0,
        ds_face_slope=5,
        coriolis_coefficient=1.2,
        bank_top_elevation=0.0,
    ):
        for param, val in {
            "name": name,
            "comment": comment,
            "ds_label": ds_label,
            "us_remote_label": us_remote_label,
            "ds_remote_label": ds_remote_label,
            "weir_elevation": weir_elevation,
            "weir_breadth": weir_breadth,
            "v_slope": v_slope,
            "side_slope": side_slope,
            "upstream_crest_height": upstream_crest_height,
            "downstream_crest_height": downstream_crest_height,
            "modular_limit": modular_limit,
            "calibration_coefficient": calibration_coefficient,
            "ds_face_slope": ds_face_slope,
            "coriolis_coefficient": coriolis_coefficient,
            "bank_top_elevation": bank_top_elevation,
        }.items():
            setattr(self, param, val)


class OUTFALL(Unit):
    """Class to hold and process OUTFALL unit type

    Args:
        name (str, optional): Unit name.
        comment (str, optional): Comment included in unit.
        flapped (bool, optional): ``True`` if outfall is flapped, ``False`` if outfall is open
        ds_label (str, optional): Downstream label
        invert (float, optional): Throat invert level
        soffit (float, optional): Throat soffit level
        bore_area (float, optional): Cross sectional area of throat opening
        upstream_sill (float, optional): Upstream sill level
        downstream_sill (float, optional): Downstream sill level
        shape (str, optional): Shape of outfall aperture ('RECTANGLE' or 'CIRCULAR')
        weir_flow (float, optional): Calibration factor for weir flow
        surcharged_flow (float, optional): Calibration factor for surcharged flow
        modular_limit (float, optional): Ratio of upstream and downstream heads when switching between free and drowned mode


    Returns:
        OUTFALL: Flood Modeller OUTFALL Unit class object
    """

    _unit = "OUTFALL"

    def _read(self, block):
        """Function to read a given OUTFALL block and store data as class attributes"""
        self._subtype = self._get_first_word(block[1])
        self.flapped = self.subtype == "FLAPPED"

        # Extends label line to be correct length before splitting to pick up blank labels
        labels = split_n_char(f"{block[2]:<{2*self._label_len}}", self._label_len)
        self.name = labels[0]
        self.ds_label = labels[1]
        self.comment = self._remove_unit_name(block[0])

        # First parameter line
        params1 = split_10_char(f"{block[3]:<60}")
        self.invert = to_float(params1[0])
        self.soffit = to_float(params1[1])
        self.bore_area = to_float(params1[2])
        self.upstream_sill = to_float(params1[3])
        self.downstream_sill = to_float(params1[4])
        self.shape = to_str(params1[5], "RECTANGLE")

        # Second parameter line
        params2 = split_10_char(block[4])
        self.weir_flow = to_float(params2[0], 1.0)
        self.surcharged_flow = to_float(params2[1], 1.0)
        self.modular_limit = to_float(params2[2], 0.7)

    def _write(self):
        """Function to write a valid OUTFALL block"""
        _validate_unit(self)  # Function to check the params are valid for CONDUIT unit
        header = self._create_header()
        labels = join_n_char_ljust(self._label_len, self.name, self.ds_label)

        self._subtype = "FLAPPED" if self.flapped else "OPEN"
        block = [header, self.subtype, labels]

        # First parameter line
        params1 = join_10_char(
            self.invert,
            self.soffit,
            self.bore_area,
            self.upstream_sill,
            self.downstream_sill,
            self.shape,
        )

        # Second parameter line
        params2 = join_10_char(self.weir_flow, self.surcharged_flow, self.modular_limit)

        block.extend([params1, params2])

        return block

    def _create_from_blank(  # noqa: PLR0913
        self,
        name="new_outfall",
        flapped=False,
        ds_label="",
        comment="",
        invert=0.0,
        soffit=0.0,
        bore_area=1.0,
        upstream_sill=0.0,
        downstream_sill=0.0,
        shape="RECTANGLE",
        weir_flow=1.0,
        surcharged_flow=1.0,
        modular_limit=0.7,
    ):
        for param, val in {
            "name": name,
            "flapped": flapped,
            "ds_label": ds_label,
            "comment": comment,
            "invert": invert,
            "soffit": soffit,
            "bore_area": bore_area,
            "upstream_sill": upstream_sill,
            "downstream_sill": downstream_sill,
            "shape": shape,
            "weir_flow": weir_flow,
            "surcharged_flow": surcharged_flow,
            "modular_limit": modular_limit,
        }.items():
            setattr(self, param, val)


class FLOODPLAIN(Unit):
    """Class to hold and process FLOODPLAIN unit type.

    Args:
        name (str, optional): FLOODPLAIN section name
        comment (str, optional): Comment included in unit
        ds_label (str, optional): Downstream node label
        data (pandas.Dataframe, optional): Dataframe object containing all the floodplain section data as well as all other relevant data.
            Columns are ``'X', 'Y', 'Mannings n', 'Easting', 'Northing'``
        calibration_coefficient (float, optional): Weir coefficient (includes discharge, velocity and calibration coefficients, optional)
        modular_limit (float, optional): Ratio of upstream and downstream heads when switching between free and drowned mode
        upstream_separation (float, optional): Distance from centre of upstream cell to section (m)
        downstream_separation (float, optional): Distance from section to centre of downstream cell (m)
        force_friction_flow (bool, optional): Force friction flow for all segments
        ds_area_constraint (float, optional): Minimum value of downstream area (relative to upstream area) when Manning's equation applies. Typical value 0.1.

    Returns:
        FLOODPLAIN: Flood Modeller FLOODPLAIN Unit class object
    """

    _unit = "FLOODPLAIN"
    _required_columns = (
        "X",
        "Y",
        "Mannings n",
        "Easting",
        "Northing",
    )

    def _read(self, fp_block):
        """Function to read a given FLOODPLAIN block and store data as class attributes."""

        self._subtype = self._get_first_word(fp_block[1])
        # Extends label line to be correct length before splitting to pick up blank labels
        labels = split_n_char(f"{fp_block[2]:<{7 * self._label_len}}", self._label_len)
        self.name = labels[0]
        self.ds_label = labels[1]
        self.comment = self._remove_unit_name(fp_block[0])

        params = split_10_char(f"{fp_block[3]:<60}")
        self.calibration_coefficient = to_float(params[0])
        self.modular_limit = to_float(params[1])
        self.upstream_separation = to_float(params[2])
        self.downstream_separation = to_float(params[3])
        self.force_friction_flow = params[4].upper() == "FRICTION"
        self.ds_area_constraint = to_float(params[5])

        self.nrows = int(split_10_char(fp_block[4])[0])
        data_list = []
        for row in fp_block[5:]:
            row_split = split_10_char(f"{row:<50}")
            x = to_float(row_split[0])  # chainage
            y = to_float(row_split[1])  # elevation
            n = to_float(row_split[2])  # Mannings
            easting = to_float(row_split[3])  # easting
            northing = to_float(row_split[4])  # northing

            data_list.append(
                [
                    x,
                    y,
                    n,
                    easting,
                    northing,
                ],
            )
        self._data = pd.DataFrame(
            data_list,
            columns=self._required_columns,
        )

    def _write(self):
        """Function to write a valid FLOODPLAIN block"""

        # Function to check the params are valid for FLOODPLAIN SECTION unit
        _validate_unit(self)
        header = self._create_header()
        labels = join_n_char_ljust(self._label_len, self.name, self.ds_label)
        # Manual so slope can have more sf
        params = join_10_char(
            self.calibration_coefficient,
            self.modular_limit,
            self.upstream_separation,
            self.downstream_separation,
            "FRICTION" if self.force_friction_flow else "",
            self.ds_area_constraint,
        )
        self.nrows = len(self._data)
        return [header, self.subtype, labels, params, *write_dataframe(self.nrows, self._data)]

    def _create_from_blank(  # noqa: PLR0913
        self,
        name="new_floodplain",
        comment="",
        ds_label="",
        data=None,
        calibration_coefficient=1.0,
        modular_limit=0.8,
        upstream_separation=0.0,
        downstream_separation=0.0,
        force_friction_flow=False,
        ds_area_constraint=0.1,
    ):
        # Initiate new FLOODPLAIN (currently hardcoding this as default)
        self._subtype = "SECTION"

        for param, val in {
            "name": name,
            "comment": comment,
            "ds_label": ds_label,
            "calibration_coefficient": calibration_coefficient,
            "modular_limit": modular_limit,
            "upstream_separation": upstream_separation,
            "downstream_separation": downstream_separation,
            "force_friction_flow": force_friction_flow,
            "ds_area_constraint": ds_area_constraint,
        }.items():
            setattr(self, param, val)

        self._data = self._enforce_dataframe(data, self._required_columns)

    @property
    def data(self) -> pd.DataFrame:
        """Data table for the FLOODPLAIN cross section.

        Returns:
            pd.DataFrame: Pandas dataframe for the cross section data with columns: 'X', 'Y',
            'Mannings n','Easting', 'Northing'
        """
        return self._data

    @data.setter
    def data(self, new_df: pd.DataFrame) -> None:
        if not isinstance(new_df, pd.DataFrame):
            msg = "The updated data table for a floodplain section must be a pandas DataFrame."
            raise TypeError(msg)
        if list(map(str.lower, new_df.columns)) != list(map(str.lower, self._required_columns)):
            msg = f"The DataFrame must only contain columns: {self._required_columns}"
            raise ValueError(msg)
        self._data = new_df
