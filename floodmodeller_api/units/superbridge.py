from __future__ import annotations

from typing import TYPE_CHECKING

from . import _helpers as h
from ._base import Unit

if TYPE_CHECKING:
    import pandas as pd


class SUPERBRIDGE(Unit):
    _unit = "SUPERBRIDGE"

    # attributes set in set_bridge_params
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

        self._subtype = br_block[4].strip()

        h.set_bridge_params(self, br_block[5])

        end_idx = 9
        self.section_nrows: list[int] = []
        self.section_data: list[pd.DataFrame] = []
        for _ in range(4):
            nrows, end_idx, data = h.read_dataframe_from_lines(
                br_block,
                end_idx,
                h.read_bridge_cross_sections,
            )
            self.section_nrows.append(nrows)
            self.section_data.append(data)

        end_idx += 1
        self.opening_nrows = h.get_int(br_block[end_idx])
        end_idx += 1
        self.opening_data: list[pd.DataFrame] = []
        for _ in range(self.opening_nrows):
            nrows, end_idx, data = h.read_dataframe_from_lines(
                br_block,
                end_idx,
                h.read_superbridge_opening_data,
            )
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
        self.block_method = block_params[3]
        self.override = block_params[4] == "OVERRIDE"
        self.block_nrows, end_idx, self.block_data = h.read_dataframe_from_lines(
            br_block,
            end_idx,
            h.read_superbridge_block_data,
        )
