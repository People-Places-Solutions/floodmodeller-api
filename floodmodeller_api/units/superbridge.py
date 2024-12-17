from __future__ import annotations

from typing import TYPE_CHECKING

from floodmodeller_api.validation import _validate_unit

from . import _helpers as h
from ._base import Unit

if TYPE_CHECKING:
    import pandas as pd


class SUPERBRIDGE(Unit):
    _unit = "SUPERBRIDGE"

    # attributes set in set_bridge_params (for mypy)
    calibration_coefficient: float
    skew: float
    bridge_width_dual: float
    bridge_dist_dual: float
    total_pier_width: float
    orifice_flow: bool
    orifice_lower_transition_dist: float
    orifice_upper_transition_dist: float
    orifice_discharge_coefficient: float

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
        line_9 = "ALIGNED" if self.aligned else ""
        line_10_11_12_13 = h.write_dataframes(None, self.section_nrows, self.section_data)
        line_14 = self.opening_type
        line_15 = h.write_dataframes(self.opening_nrows, self.opening_nsubrows, self.opening_data)
        line_16 = h.write_dataframe(self.culvert_nrows, self.culvert_data)
        line_17 = h.write_dataframe(
            h.join_10_char(self.spill_nrows, self.weir_coefficient, self.modular_limit),
            self.spill_data,
        )
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
            # 7
            # 8
            line_9,
            *line_10_11_12_13,
            line_14,
            *line_15,
            *line_16,
            *line_17,
            # 18
            *line_19,
        ]
