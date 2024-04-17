"""
Flood Modeller Python API
Copyright (C) 2024 Jacobs U.K. Limited

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see https://www.gnu.org/licenses/.

If you have any query about this program or this License, please contact us at support@floodmodeller.com or write to the following
address: Jacobs UK Limited, Flood Modeller, Cottons Centre, Cottons Lane, London, SE1 2QG, United Kingdom.
"""

import pandas as pd

from floodmodeller_api.validation import _validate_unit

from ._base import Unit
from .helpers import (
    _to_float,
    _to_int,
    _to_str,
    join_10_char,
    join_12_char_ljust,
    join_n_char_ljust,
    split_10_char,
    split_n_char,
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

    def _read(self, br_block):  # noqa: C901, PLR0912, PLR0915
        """Function to read a given BRIDGE block and store data as class attributes"""
        self._subtype = br_block[1].split(" ")[0].strip()
        # Extends label line to be correct length before splitting to pick up blank labels
        labels = split_n_char(f"{br_block[2]:<{4*self._label_len}}", self._label_len)
        self.name = labels[0]
        self.ds_label = labels[1]
        self.us_remote_label = labels[2]
        self.ds_remote_label = labels[3]
        self.comment = br_block[0].replace("BRIDGE", "").strip()

        # Read ARCH type unit
        if self.subtype == "ARCH":
            # Read Params
            params = split_10_char(f"{br_block[4]:<90}")
            self.calibration_coefficient = _to_float(params[0], 1.0)
            self.skew = _to_float(params[1])
            self.bridge_width_dual = _to_float(params[2])
            self.bridge_dist_dual = _to_float(params[3])
            if params[5] == "ORIFICE":
                self.orifice_flow = True
            else:
                self.orifice_flow = False
            self.orifice_lower_transition_dist = _to_float(params[6])
            self.orifice_upper_transition_dist = _to_float(params[7])
            self.orifice_discharge_coefficient = _to_float(params[8], 1.0)

            # Read cross section data
            self.section_nrows = int(split_10_char(br_block[5])[0])
            data_list = []
            for row in br_block[6 : 6 + self.section_nrows]:
                row_split = split_10_char(f"{row:<50}")
                x = _to_float(row_split[0])  # chainage
                y = _to_float(row_split[1])  # elevation
                n = _to_float(row_split[2])  # Mannings
                embankment = row_split[4]  # Embankment flag
                data_list.append([x, y, n, embankment])
            self.section_data = pd.DataFrame(
                data_list,
                columns=["X", "Y", "Mannings n", "Embankments"],
            )

            # Read bridge opening data
            self.opening_nrows = int(split_10_char(br_block[6 + self.section_nrows])[0])
            data_list = []
            for row in br_block[6 + self.section_nrows + 1 :]:
                row_split = split_10_char(f"{row:<40}")
                start = _to_float(row_split[0])  # Start (m)
                finish = _to_float(row_split[1])  # Finish (m)
                spring = _to_float(row_split[2])  # Springing Level
                soffit = _to_float(row_split[3])  # Soffit Level
                data_list.append([start, finish, spring, soffit])
            self.opening_data = pd.DataFrame(
                data_list,
                columns=["Start", "Finish", "Springing Level", "Soffit Level"],
            )

        # Read USBPR type unit
        elif self.subtype == "USBPR1978":
            # Read Params
            params = split_10_char(f"{br_block[4]:<90}")
            self.calibration_coefficient = _to_float(params[0], 1.0)
            self.skew = _to_float(params[1])
            self.bridge_width_dual = _to_float(params[2])
            self.bridge_dist_dual = _to_float(params[3])
            self.total_pier_width = _to_float(params[4])
            if params[5] == "ORIFICE":
                self.orifice_flow = True
            else:
                self.orifice_flow = False
            self.orifice_lower_transition_dist = _to_float(params[6])
            self.orifice_upper_transition_dist = _to_float(params[7])
            self.orifice_discharge_coefficient = _to_float(params[8], 1.0)

            self.abutment_type = split_10_char(br_block[5])[0]
            self.abutment_alignment = split_10_char(br_block[7])[0]

            pier_info = split_10_char(f"{br_block[6]:<40}")
            if int(pier_info[0]) > 0:
                self.specify_piers = True
                self.npiers = int(pier_info[0])
                if pier_info[1] == "COEF":
                    self.pier_use_calibration_coeff = True
                    self.pier_calibration_coeff = _to_float(pier_info[3])
                else:
                    self.pier_use_calibration_coeff = False
                    self.pier_shape = pier_info[1]
                    self.pier_faces = pier_info[2]
            else:
                self.specify_piers = False
                self.soffit_shape = pier_info[1]

            # Read cross section data
            self.section_nrows = int(split_10_char(br_block[8])[0])
            data_list = []
            for row in br_block[9 : 9 + self.section_nrows]:
                row_split = split_10_char(f"{row:<50}")
                x = _to_float(row_split[0])  # chainage
                y = _to_float(row_split[1])  # elevation
                n = _to_float(row_split[2])  # Mannings
                embankment = row_split[4]  # Embankment flag
                data_list.append([x, y, n, embankment])
            self.section_data = pd.DataFrame(
                data_list,
                columns=["X", "Y", "Mannings n", "Embankments"],
            )

            # Read bridge opening data
            self.opening_nrows = int(split_10_char(br_block[9 + self.section_nrows])[0])
            data_list = []
            start_row = 9 + self.section_nrows + 1
            end_row = start_row + self.opening_nrows
            for row in br_block[start_row:end_row]:
                row_split = split_10_char(f"{row:<40}")
                start = _to_float(row_split[0])  # Start (m)
                finish = _to_float(row_split[1])  # Finish (m)
                spring = _to_float(row_split[2])  # Springing Level
                soffit = _to_float(row_split[3])  # Soffit Level
                data_list.append([start, finish, spring, soffit])
            self.opening_data = pd.DataFrame(
                data_list,
                columns=["Start", "Finish", "Springing Level", "Soffit Level"],
            )

            # Read flood relief culvert data
            self.culvert_nrows = int(
                split_10_char(br_block[9 + self.section_nrows + self.opening_nrows + 1])[0],
            )
            data_list = []
            start_row = 9 + self.section_nrows + self.opening_nrows + 2
            end_row = start_row + self.culvert_nrows
            for row in br_block[start_row:end_row]:
                row_split = split_10_char(f"{row:<60}")
                invert = _to_float(row_split[0])  # Invert
                soffit = _to_float(row_split[1])  # Soffit
                area = _to_float(row_split[2])  # Section Area
                cd_part = _to_float(row_split[3])  # Cd Part Full
                cd_full = _to_float(row_split[4])  # Cd Full
                drown = _to_float(row_split[5])  # Drowning Coefficient
                data_list.append([invert, soffit, area, cd_part, cd_full, drown])
            self.culvert_data = pd.DataFrame(
                data_list,
                columns=[
                    "Invert",
                    "Soffit",
                    "Section Area",
                    "Cd Part Full",
                    "Cd Full",
                    "Drowning Coefficient",
                ],
            )

        # Read Pierloss type bridge
        elif self.subtype == "PIERLOSS":
            # Read Params
            params = split_10_char(f"{br_block[4]:<50}")
            self.calibration_coefficient = _to_float(params[0], 1.0)
            if params[1] == "ORIFICE":
                self.orifice_flow = True
            else:
                self.orifice_flow = False
            self.orifice_lower_transition_dist = _to_float(params[3])
            self.orifice_upper_transition_dist = _to_float(params[4])
            self.orifice_discharge_coefficient = _to_float(params[2], 1.0)
            additional_params = split_10_char(f"{br_block[5]:<20}")
            self.pier_coefficient = _to_float(additional_params[0], 0.9)
            self.bridge_width = _to_float(additional_params[1])

            # Read US cross section data
            self.us_section_nrows = int(split_10_char(br_block[6])[0])
            data_list = []
            for row in br_block[7 : 7 + self.us_section_nrows]:
                row_split = split_10_char(f"{row:<60}")
                x = _to_float(row_split[0])  # chainage
                y = _to_float(row_split[1])  # elevation
                n = _to_float(row_split[2])  # Mannings
                embankment = row_split[4]  # Embankment flag
                top_level = row_split[5]  # Top Level (m)
                data_list.append([x, y, n, embankment, top_level])
            self.us_section_data = pd.DataFrame(
                data_list,
                columns=["X", "Y", "Mannings n", "Embankments", "Top Level"],
            )

            # Read DS cross section data
            new_idx = 6 + 1 + self.us_section_nrows
            self.ds_section_nrows = int(split_10_char(br_block[new_idx])[0])
            data_list = []
            for row in br_block[new_idx + 1 : new_idx + 1 + self.ds_section_nrows]:
                row_split = split_10_char(f"{row:<60}")
                x = _to_float(row_split[0])  # chainage
                y = _to_float(row_split[1])  # elevation
                n = _to_float(row_split[2])  # Mannings
                embankment = row_split[4]  # Embankment flag
                top_level = row_split[5]  # Top Level (m)
                data_list.append([x, y, n, embankment, top_level])
            self.ds_section_data = pd.DataFrame(
                data_list,
                columns=["X", "Y", "Mannings n", "Embankments", "Top Level"],
            )

            # Read pier locations
            new_idx += 1 + self.ds_section_nrows
            self.pier_locs_nrows = int(split_10_char(br_block[new_idx])[0])
            data_list = []
            for row in br_block[new_idx + 1 : new_idx + 1 + self.pier_locs_nrows]:
                row_split = split_10_char(f"{row:<40}")
                l_x = _to_float(row_split[0])  # chainage
                l_top_level = _to_float(row_split[1])  # Top Level (m)
                r_x = _to_float(row_split[2])  # chainage
                r_top_level = _to_float(row_split[3])  # Top Level (m)
                data_list.append([l_x, l_top_level, r_x, r_top_level])
            self.pier_locs_data = pd.DataFrame(
                data_list,
                columns=["Left X", "Left Top Level", "Right X", "Right Top Level"],
            )

        else:
            # This else block is triggered for bridge subtypes which aren't yet supported, and just keeps the 'br_block' in it's raw state to write back.
            print(
                f'This Bridge sub-type: "{self.subtype}" is currently unsupported for reading/editing',
            )
            self._raw_block = br_block
            self.name = br_block[2][:12].strip()

    def _write(self):  # noqa: C901, PLR0912, PLR0915
        """Function to write a valid BRIDGE block"""
        _validate_unit(self)  # Function to check the params are valid for BRIDGE unit
        header = "BRIDGE " + self.comment
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
            self.section_nrows = len(self.section_data)
            br_block.extend(["MANNING", params, f"{str(self.section_nrows):>10}"])

            section_data = []
            for _, x, y, n, embankments in self.section_data.itertuples():
                # Adding extra 10 spaces before embankment flag
                row = join_10_char(x, y, n, "")
                row += embankments
                section_data.append(row)

            br_block.extend(section_data)

            self.opening_nrows = len(self.opening_data)
            br_block.append(f"{str(self.opening_nrows):>10}")
            opening_data = []
            for _, start, finish, spring, soffit in self.opening_data.itertuples():
                row = join_10_char(start, finish, spring, soffit)
                opening_data.append(row)

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
                    pier_params = f'{self.npiers:>10}{"COEF":<10}{"":>10}{self.calibration_coefficient:>10.3f}'
                else:
                    pier_params = f"{self.npiers:>10}{self.pier_shape:<10}{self.pier_faces:<10}"
            else:
                pier_params = f"{0:>10}{self.soffit_shape}"

            self.section_nrows = len(self.section_data)
            br_block.extend(
                [
                    "MANNING",
                    params,
                    f"{str(self.abutment_type):>10}",
                    pier_params,
                    self.abutment_alignment,
                    f"{str(self.section_nrows):>10}",
                ],
            )

            section_data = []
            for _, x, y, n, embankments in self.section_data.itertuples():
                # Adding extra 10 spaces before embankment flag
                row = join_10_char(x, y, n, "")
                row += embankments
                section_data.append(row)
            br_block.extend(section_data)

            self.opening_nrows = len(self.opening_data)
            br_block.append(f"{str(self.opening_nrows):>10}")
            opening_data = []
            for _, start, finish, spring, soffit in self.opening_data.itertuples():
                row = join_10_char(start, finish, spring, soffit)
                opening_data.append(row)
            br_block.extend(opening_data)

            self.culvert_nrows = len(self.culvert_data)
            br_block.append(f"{str(self.culvert_nrows):>10}")
            culvert_data = []
            for (
                _,
                invert,
                soffit,
                area,
                cd_part,
                cd_full,
                drown,
            ) in self.culvert_data.itertuples():
                row = join_10_char(invert, soffit, area, cd_part, cd_full, drown)
                culvert_data.append(row)
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
            self.us_section_nrows = len(self.us_section_data)
            br_block.extend(
                [
                    "YARNELL",
                    params,
                    additional_params,
                    f"{str(self.us_section_nrows):>10}",
                ],
            )

            us_section_data = []
            for _, x, y, n, embankments, top_level in self.us_section_data.itertuples():
                # Adding extra 10 spaces before embankment flag
                row = join_10_char(x, y, n, "")
                row += f"{embankments:<10}"
                row += join_10_char(top_level)
                us_section_data.append(row)
            br_block.extend(us_section_data)

            self.ds_section_nrows = len(self.ds_section_data)
            br_block.append(f"{str(self.ds_section_nrows):>10}")
            ds_section_data = []
            for _, x, y, n, embankments, top_level in self.ds_section_data.itertuples():
                # Adding extra 10 spaces before embankment flag
                row = join_10_char(x, y, n, "")
                row += f"{embankments:<10}"
                row += join_10_char(top_level)
                ds_section_data.append(row)
            br_block.extend(ds_section_data)

            self.pier_locs_nrows = len(self.pier_locs_data)
            br_block.append(f"{str(self.pier_locs_nrows):>10}")
            pier_locs_data = []
            for (
                _,
                l_x,
                l_top_level,
                r_x,
                r_top_level,
            ) in self.pier_locs_data.itertuples():
                row = join_10_char(l_x, l_top_level, r_x, r_top_level)
                pier_locs_data.append(row)
            br_block.extend(pier_locs_data)

            return br_block

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
        self._subtype = block[1].split(" ")[0].strip()

        # Extends label line to be correct length before splitting to pick up blank labels
        labels = split_n_char(f"{block[2]:<{3*self._label_len}}", self._label_len)
        self.name = labels[0]
        self.ds_label = labels[1]
        self.remote_label = labels[2]
        self.comment = block[0].replace("SLUICE", "").strip()

        # First parameter line
        params1 = split_10_char(f"{block[3]:<80}")
        self.weir_flow_coefficient = _to_float(params1[0], 1.0)
        self.under_gate_flow = _to_float(params1[1], 1.0)
        self.weir_breadth = _to_float(params1[2])
        self.crest_elevation = _to_float(params1[3])
        self.gate_height_or_chord = _to_float(params1[4])
        self.weir_length = _to_float(params1[5])
        if self.subtype == "RADIAL":
            self.use_degrees = params1[6] == "DEGREES"
            self.allow_free_flow_under = params1[7] == "FREESLUICE"

        # Second parameter line
        params2 = split_10_char(f"{block[4]:<70}")
        self.us_weir_height = _to_float(params2[0])
        self.ds_weir_height = _to_float(params2[1])
        self.bias_factor = _to_float(params2[2], 1.0)
        self.over_gate_flow = _to_float(params2[3], 1.0)
        if self.subtype == "RADIAL":
            self.pivot_height = _to_float(params2[4], 0.7)
            self.gate_radius = _to_float(params2[5], 0.7)
        else:
            self.modular_limits = {
                "weir_flow": _to_float(params2[4]),
                "under_gate_flow": _to_float(params2[5], 1.0),
                "over_gate_flow": _to_float(params2[6], 1.0),
            }

        # Third parameter line
        params3 = split_10_char(f"{block[5]:<60}")
        self.ngates = int(params3[0])  # number of gates
        if self.subtype == "RADIAL":
            self.modular_limits = {
                "weir_flow": _to_float(params3[1]),
                "under_gate_flow": _to_float(params3[2], 1.0),
                "over_gate_flow": _to_float(params3[3], 1.0),
            }
            self.timeunit = _to_str(params3[4], "SECONDS", check_float=True)
            self.extendmethod = _to_str(params3[5], "EXTEND")
        else:
            self.timeunit = _to_str(params3[1], "SECONDS", check_float=True)
            self.extendmethod = _to_str(params3[2], "EXTEND")

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
            print(
                f"Note: Sluice control using method: {self.control_method} is not currently supported.",
            )

    def _write(self):
        """Function to write a valid SLUICE block"""
        _validate_unit(self)  # Function to check the params are valid for CONDUIT unit
        header = "SLUICE " + self.comment
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
        self.ngates = len(self.gates)
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
                    x = _to_float(row_split[0])  # time
                    y = _to_float(row_split[1])  # opening
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
                    x = _to_float(row_split[0])  # time
                    y = row_split[1]  # mode
                    z = _to_float(row_split[2])  # opening
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
        self._subtype = block[1].split(" ")[0].strip()
        self.flapped = self.subtype == "FLAPPED"

        # Extends label line to be correct length before splitting to pick up blank labels
        labels = split_n_char(f"{block[2]:<{2*self._label_len}}", self._label_len)
        self.name = labels[0]
        self.ds_label = labels[1]
        self.comment = block[0].replace("ORIFICE", "").strip()

        # First parameter line
        params1 = split_10_char(f"{block[3]:<60}")
        self.invert = _to_float(params1[0])
        self.soffit = _to_float(params1[1])
        self.bore_area = _to_float(params1[2])
        self.upstream_sill = _to_float(params1[3])
        self.downstream_sill = _to_float(params1[4])
        self.shape = _to_str(params1[5], "RECTANGLE")

        # Second parameter line
        params2 = split_10_char(block[4])
        self.weir_flow = _to_float(params2[0], 1.0)
        self.surcharged_flow = _to_float(params2[1], 1.0)
        self.modular_limit = _to_float(params2[2], 0.7)

    def _write(self):
        """Function to write a valid ORIFICE block"""
        _validate_unit(self)  # Function to check the params are valid for CONDUIT unit
        header = "ORIFICE " + self.comment
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
        self.comment = block[0].replace("SPILL", "").strip()

        # First parameter line
        params = split_10_char(block[2])
        self.weir_coefficient = _to_float(params[0], 1.2)
        self.modular_limit = _to_float(params[1], 0.9)

        # Spill section data
        data_list = []
        for row in block[4:]:
            row_split = split_10_char(f"{row:<40}")
            x = _to_float(row_split[0])  # chainage
            y = _to_float(row_split[1])  # elevation
            e = _to_float(row_split[2])  # easting
            n = _to_float(row_split[3])  # northing

            data_list.append([x, y, e, n])

        spill_data = pd.DataFrame(data_list, columns=["X", "Y", "Easting", "Northing"])
        self.data = spill_data

    def _write(self):
        """Function to write a valid SPILL block"""
        _validate_unit(self)  # Function to check the params are valid for CONDUIT unit
        header = "SPILL " + self.comment
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
        self.comment = block[0].replace("RNWEIR", "").strip()

        # First parameter line
        params1 = split_10_char(f"{block[2]:<50}")
        self.velocity_coefficient = _to_float(params1[0])
        self.weir_length = _to_float(params1[1])
        self.weir_breadth = _to_float(params1[2])
        self.weir_elevation = _to_float(params1[3])
        self.modular_limit = _to_float(params1[4])

        # Second parameter line
        params2 = split_10_char(f"{block[3]:<20}")
        self.upstream_crest_height = _to_float(params2[0])
        self.downstream_crest_height = _to_float(params2[1])

    def _write(self):
        """Function to write a valid RNWEIR block"""
        _validate_unit(self)
        header = "RNWEIR " + self.comment
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
        self.comment = block[0].replace("WEIR", "").strip()

        # Exponent
        self.exponent = _to_float(block[2].strip())

        # Parameters line
        params = split_10_char(f"{block[3]:<50}")
        self.discharge_coefficient = _to_float(params[0])
        self.velocity_coefficient = _to_float(params[1])
        self.weir_breadth = _to_float(params[2])
        self.weir_elevation = _to_float(params[3])
        self.modular_limit = _to_float(params[4])

    def _write(self):
        """Function to write a valid WEIR block"""
        _validate_unit(self)
        header = "WEIR " + self.comment
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
        self.comment = block[0].replace("CRUMP", "").strip()

        # First parameter line
        params1 = split_10_char(f"{block[2]:<40}")
        self.calibration_coefficient = _to_float(params1[0])
        self.weir_breadth = _to_float(params1[1])
        self.weir_elevation = _to_float(params1[2])
        self.modular_limit = _to_float(params1[3])

        # Second parameter line
        params2 = split_10_char(f"{block[3]:<20}")
        self.upstream_crest_height = _to_float(params2[0])
        self.downstream_crest_height = _to_float(params2[1])

    def _write(self):
        """Function to write a valid CRUMP block"""
        _validate_unit(self)
        header = "CRUMP " + self.comment
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
        self.comment = block[0].replace("FLAT-V WEIR", "").strip()

        # First parameter line
        params1 = split_10_char(f"{block[2]:<90}")
        self.calibration_coefficient = _to_float(params1[0])
        self.weir_breadth = _to_float(params1[1])
        self.weir_elevation = _to_float(params1[2])
        self.modular_limit = _to_float(params1[3])
        self.v_slope = _to_float(params1[4])
        self.side_slope = _to_float(params1[5])
        self.ds_face_slope = _to_float(params1[6])
        self.coriolis_coefficient = _to_float(params1[7])
        self.bank_top_elevation = _to_float(params1[8])

        # Second parameter line
        params2 = split_10_char(f"{block[3]:<20}")
        self.upstream_crest_height = _to_float(params2[0])
        self.downstream_crest_height = _to_float(params2[1])

    def _write(self):
        """Function to write a valid FLAT-V WEIR block"""

        _validate_unit(self)
        header = "FLAT-V WEIR " + self.comment
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


class RESERVOIR(Unit):  # NOT CURRENTLY IN USE
    """Class to hold and process RESERVOIR unit type

    Args:
        name (str, optional): Unit name.
        comment (str, optional): Comment included in unit.
        all_labels (str, optional): Unlimited number of labels - not including first label (name).
        easting (float, optional): Easting coordinate of reservoir reference point (not used in computations).
        northing (float, optional): Northing coordinate of reservoir reference point (not used in computations).
        runoff_factor (float, optional): Rainfall runoff factor.
        num_pairs (float, optional): Number of elevation/area pairs.
        lat1 (str, optional): First lateral inflow label.
        lat2 (str, optional): Second lateral inflow label.
        lat3 (str, optional): Third lateral inflow label.
        lat4 (str, optional): Fourth lateral inflow label.
        data (pandas.DataFrame): Dataframe object containing all the reservoir section data.
            Columns are ``'Elevation','Plan Area'``

    Returns:
        RESERVOIR: Flood Modeller RESERVOIR Unit class object"""

    _unit = "RESERVOIR"

    def _read(self, block):
        """Function to read a given RESERVOIR WEIR block and store data as class attributes"""

        # Extends label line to be correct length before splitting to pick up blank labels
        num_labels = len(block[1]) // self._label_len
        labels = split_n_char(f"{block[1]:<{num_labels*self._label_len}}", self._label_len)
        self.name = labels[0]
        self.all_labels = labels[0 : len(labels)]
        self.comment = block[0].replace("RESERVOIR", "").strip()

        # Option 1 (runs if comment == "#revision#1")
        if self.comment == "#revision#1":
            # Lateral inflow labels
            lateral_labels = split_n_char(f"{block[2]:<{4*self._label_len}}", self._label_len)
            self.lat1 = lateral_labels[0]
            self.lat2 = lateral_labels[1]
            self.lat3 = lateral_labels[2]
            self.lat4 = lateral_labels[3]

            # Number of pairs of data
            self.num_pairs = _to_int(block[3])

            # Reservoir section data
            data_list = []
            for row in block[4 : len(block) - 1]:
                row_split = split_10_char(f"{row:<20}")
                elevation = _to_float(row_split[0])  # elevation
                plan_area = _to_float(row_split[1])  # plan area
                data_list.append([elevation, plan_area])
            reservoir_data = pd.DataFrame(data_list, columns=["Elevation", "Plan Area"])
            self.data = reservoir_data

            # Coordinate data
            coordinate_data = split_n_char(
                f"{block[len(block)-1]:<{3*self._label_len}}",
                self._label_len,
            )
            self.easting = _to_float(coordinate_data[0])
            self.northing = _to_float(coordinate_data[1])
            self.runoff_factor = _to_float(coordinate_data[2])
        else:  # Option 2 (runs if comment != "#revision#1")
            # Number of pairs of data
            self.num_pairs = _to_int(block[2])

            # Reservoir section data
            data_list = []
            for row in block[3:]:
                row_split = split_10_char(f"{row:<20}")
                elevation = _to_float(row_split[0])  # elevation
                plan_area = _to_float(row_split[1])  # plan area
                data_list.append([elevation, plan_area])
            reservoir_data = pd.DataFrame(data_list, columns=["Elevation", "Plan Area"])
            self.data = reservoir_data

    def _write(self):
        """Function to write a valid RESERVOIR block"""

        _validate_unit(self)
        header = "RESERVOIR " + self.comment
        self.labels = "          ".join(self.all_labels)
        block = [header, self.labels]

        # Option 1 (runs if comment == "#revision#1")
        if self.comment == "#revision#1":
            # Lateral inflow labels
            lat_labels = join_12_char_ljust(self.lat1, self.lat2, self.lat3, self.lat4)
            block.append(lat_labels)

            # Number of pairs of data
            block.append(join_12_char_ljust(self.num_pairs))

            # Reservoir section data
            section_data = [
                join_12_char_ljust(elevation, plan_area)
                for _, elevation, plan_area, in self.data.itertuples()
            ]
            block.extend(section_data)

            # Coordinate data
            coords = join_12_char_ljust(self.easting, self.northing, self.runoff_factor)
            block.append(coords)
        else:  # Option 2 (runs if comment != "#revision#1")
            # Number of pairs of data
            block.append(join_12_char_ljust(self.num_pairs))

            # Reservoir section data
            section_data = [
                join_12_char_ljust(elevation, plan_area)
                for _, elevation, plan_area, in self.data.itertuples()
            ]
            block.extend(section_data)

        return block

    def _create_from_blank(  # noqa: PLR0913
        self,
        name="new_reservoir",
        comment="",
        easting=0.0,
        northing=0.0,
        runoff_factor=0.0,
        num_pairs=1,
        data=None,
        lat1="",
        lat2="",
        lat3="",
        lat4="",
    ):
        for param, val in {
            "name": name,
            "comment": comment,
            "easting": easting,
            "northing": northing,
            "runoff_factor": runoff_factor,
            "num_pairs": num_pairs,
            "lat1": lat1,
            "lat2": lat2,
            "lat3": lat3,
            "lat4": lat4,
        }.items():
            setattr(self, param, val)

        self.data = (
            data
            if isinstance(data, pd.DataFrame)
            else pd.DataFrame([[0.0, 0.0]], columns=["Elevation", "Plan Area"])
        )


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
        self._subtype = block[1].split(" ")[0].strip()
        self.flapped = self.subtype == "FLAPPED"

        # Extends label line to be correct length before splitting to pick up blank labels
        labels = split_n_char(f"{block[2]:<{2*self._label_len}}", self._label_len)
        self.name = labels[0]
        self.ds_label = labels[1]
        self.comment = block[0].replace("OUTFALL", "").strip()

        # First parameter line
        params1 = split_10_char(f"{block[3]:<60}")
        self.invert = _to_float(params1[0])
        self.soffit = _to_float(params1[1])
        self.bore_area = _to_float(params1[2])
        self.upstream_sill = _to_float(params1[3])
        self.downstream_sill = _to_float(params1[4])
        self.shape = _to_str(params1[5], "RECTANGLE")

        # Second parameter line
        params2 = split_10_char(block[4])
        self.weir_flow = _to_float(params2[0], 1.0)
        self.surcharged_flow = _to_float(params2[1], 1.0)
        self.modular_limit = _to_float(params2[2], 0.7)

    def _write(self):
        """Function to write a valid OUTFALL block"""
        _validate_unit(self)  # Function to check the params are valid for CONDUIT unit
        header = "OUTFALL " + self.comment
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
