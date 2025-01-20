from __future__ import annotations

from typing import TYPE_CHECKING

from floodmodeller_api.validation import _validate_unit

from . import _helpers as h
from ._base import Unit

if TYPE_CHECKING:
    import pandas as pd


class SUPERBRIDGE(Unit):
    """Class to hold and process SUPERBRIDGE type (from Flood Modeller v7.4).

    **Common Attributes**

    Args:
        name (str): Superbridge section name
        comment (str): Comment included in unit
        ds_label (str): Downstream label
        us_remote_label, ds_remote_label (str): Remote labels
        subtype (str): Defines the type of bridge unit (*Should not be changed*)
        spill data (pandas.DataFrame): Dataframe object representing the spill data. Columns are ``'X'``, ``'Y'``,
            ``'Easting'`` and ``'Northing'``
        block data (pandas.DataFrame): Dataframe object representing the block data. Columns are ``'percentage'``,
            ``'time'`` and ``'datetime'``

    **ARCH Type (``SUPERBRIDGE.subtype == 'ARCH'``)**

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

    **USBPR Type (``SUPERBRIDGE.subtype == 'USBPR1978'``)**

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
            ``'Soffit'``, ``'Section Area'``, ``'Cd Part Full'``, ``'Cd Full'``, ``'Drowning Coefficient'`` and ``'X'``

    **PIERLOSS Type (``SUPERBRIDGE.subtype == 'PIERLOSS'``)**

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
        NotImplementedError: Raised if class is initialised without existing Superbridge block (i.e. if attempting to create new Superbridge unit).
            This will be an option for future releases

    Returns:
        SUPERBRIDGE: Flood Modeller SUPERBRIDGE Unit class object
    """

    _unit = "SUPERBRIDGE"

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

    def _read(self, br_block: list[str]) -> None:
        self.comment = br_block[0].replace(self._unit, "").strip()

        labels = h.split_n_char(f"{br_block[1]:<{4*self._label_len}}", self._label_len)
        self.name = labels[0]
        self.ds_label = labels[1]
        self.us_remote_label = labels[2]
        self.ds_remote_label = labels[3]

        self.revision = h.to_int(br_block[2])
        self.bridge_name = br_block[3]
        self._subtype = br_block[4].strip()
        h.set_bridge_params(self, br_block[5])
        self.abutment_type = h.to_int(br_block[6])
        h.set_pier_params(self, br_block[7])
        self.aligned = br_block[8].strip() == "ALIGNED"

        end_idx = 9
        self.section_nrows: list[int] = []
        self.section_data: list[pd.DataFrame] = []
        for _ in range(4):
            nrows, end_idx, data = h.read_dataframe_from_lines(
                br_block,
                end_idx,
                h.read_bridge_cross_sections,
                include_panel_marker=True,
            )
            self.section_nrows.append(nrows)
            self.section_data.append(data)

        self.opening_type = br_block[end_idx]
        end_idx += 1
        self.opening_nrows = h.get_int(br_block[end_idx])
        end_idx += 1
        self.opening_nsubrows: list[int] = []
        self.opening_data: list[pd.DataFrame] = []
        for _ in range(self.opening_nrows):
            nrows, end_idx, data = h.read_dataframe_from_lines(
                br_block,
                end_idx,
                h.read_superbridge_opening_data,
            )
            self.opening_nsubrows.append(nrows)
            self.opening_data.append(data)

        self.culvert_nrows, end_idx, self.culvert_data = h.read_dataframe_from_lines(
            br_block,
            end_idx,
            h.read_bridge_culvert_data,
        )

        spill_params = h.split_10_char(f"{br_block[end_idx]:<30}")
        self.weir_coefficient = h.to_float(spill_params[1])
        self.modular_limit = h.to_float(spill_params[2])
        self.spill_nrows, end_idx, self.spill_data = h.read_dataframe_from_lines(
            br_block,
            end_idx,
            h.read_spill_section_data,
        )

        self.block_comment = br_block[end_idx]
        end_idx += 1
        block_params = h.split_10_char(f"{br_block[end_idx]:<50}")
        self.inlet_loss = h.to_float(block_params[1])
        self.outlet_loss = h.to_float(block_params[2])
        self.block_method = "USDEPTH" if (block_params[3] == "") else block_params[3]
        self.override = block_params[4] == "OVERRIDE"
        self.block_nrows, end_idx, self.block_data = h.read_dataframe_from_lines(
            br_block,
            end_idx,
            h.read_superbridge_block_data,
        )

    def _write(self) -> list[str]:
        _validate_unit(self)

        line_1 = self._unit + " " + self.comment
        line_2 = h.join_12_char_ljust(
            self.name,
            self.ds_label,
            self.us_remote_label,
            self.ds_remote_label,
        )
        line_3 = str(self.revision)
        line_4 = self.bridge_name
        line_5 = self.subtype
        line_6 = h.join_10_char(
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
                line_8 = h.join_10_char(
                    self.npiers,
                    "COEFF",
                    "",
                    self.pier_calibration_coeff,
                )
            else:
                line_8 = h.join_10_char(
                    self.npiers,
                    self.pier_shape,
                    self.pier_faces,
                )
        else:
            line_8 = h.join_10_char(
                0,
                self.soffit_shape,
            )
        line_9 = "ALIGNED" if self.aligned else ""
        line_10_11_12_13 = h.write_dataframes(None, self.section_nrows, self.section_data)
        line_14 = self.opening_type
        line_15 = h.write_dataframes(self.opening_nrows, self.opening_nsubrows, self.opening_data)
        line_16 = h.write_dataframe(self.culvert_nrows, self.culvert_data)
        line_17 = h.write_dataframe(
            h.join_10_char(self.spill_nrows, self.weir_coefficient, self.modular_limit),
            self.spill_data,
        )
        line_18 = self.block_comment
        line_19 = h.write_dataframe(
            h.join_10_char(
                self.block_nrows,
                self.inlet_loss,
                self.outlet_loss,
                self.block_method,
                "OVERRIDE" if self.override else "NOOVERRIDE",
            ),
            self.block_data,
        )

        return [
            line_1,
            line_2,
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
