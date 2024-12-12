from __future__ import annotations

from typing import TYPE_CHECKING

from ._base import Unit
from .helpers import (
    _to_float,
    _to_int,
    get_int,
    read_bridge_cross_sections,
    read_bridge_culvert_data,
    read_bridge_params,
    read_spill_section_data,
    read_superbridge_block_data,
    read_superbridge_opening_data,
    split_10_char,
    split_n_char,
)

if TYPE_CHECKING:
    import pandas as pd


class SUPERBRIDGE(Unit):
    _unit = "SUPERBRIDGE"

    def _read(self, br_block: list[str]):
        self.comment = br_block[0].replace(self._unit, "").strip()

        labels = split_n_char(f"{br_block[1]:<{4*self._label_len}}", self._label_len)
        self.name = labels[0]
        self.ds_label = labels[1]
        self.us_remote_label = labels[2]
        self.ds_remote_label = labels[3]

        self._subtype = br_block[4].strip()

        params = read_bridge_params(br_block[5])
        for key, val in params.items():
            setattr(self, key, val)

        end_idx = 9
        self.section_nrows: list[int] = []
        self.section_data: list[pd.DataFrame] = []
        for _ in range(4):
            section_nrows = get_int(br_block[end_idx])
            start_idx = end_idx + 1
            end_idx = start_idx + section_nrows
            section_data = read_bridge_cross_sections(br_block[start_idx:end_idx])
            self.section_nrows.append(section_nrows)
            self.section_data.append(section_data)

        end_idx += 1
        self.opening_nrows = get_int(br_block[end_idx])
        end_idx += 1
        self.opening_data: list[pd.DataFrame] = []
        for _ in range(self.opening_nrows):
            nrows = get_int(br_block[end_idx])
            start_idx = end_idx + 1
            end_idx = start_idx + nrows
            opening_data = read_superbridge_opening_data(br_block[start_idx:end_idx])
            self.opening_data.append(opening_data)

        self.culvert_nrows = get_int(br_block[end_idx])
        start_idx = end_idx + 1
        end_idx = start_idx + self.culvert_nrows
        self.culvert_data = read_bridge_culvert_data(br_block[start_idx:end_idx])

        spill_params = split_10_char(f"{br_block[end_idx]:<30}")
        self.spill_nrows = _to_int(spill_params[0])
        self.weir_coefficient = _to_float(spill_params[1])
        self.modular_limit = _to_float(spill_params[2])
        start_idx = end_idx + 1
        end_idx = start_idx + self.spill_nrows
        self.spill_data = read_spill_section_data(br_block[start_idx:end_idx])

        self.block_comment = br_block[end_idx]
        end_idx += 1
        block_params = split_10_char(f"{br_block[end_idx]:<50}")
        self.block_nrows = _to_int(block_params[0])
        self.inlet_loss = _to_float(block_params[1])
        self.outlet_loss = _to_float(block_params[2])
        self.block_method = block_params[3]
        self.override = block_params[4] == "OVERRIDE"
        start_idx = end_idx + 1
        end_idx = start_idx + self.block_nrows
        self.block_data = read_superbridge_block_data(br_block[start_idx:end_idx])
