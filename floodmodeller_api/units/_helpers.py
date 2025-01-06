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

import copy
from itertools import chain
from typing import Any, Callable

import pandas as pd

NOTATION_THRESHOLD = 10


def split_10_char(line: str) -> list[str]:
    return split_n_char(line, 10)


def split_12_char(line: str) -> list[str]:
    return split_n_char(line, 12)


def split_n_char(line: str, n: int) -> list[str]:
    return [line[i : i + n].strip() for i in range(0, len(line), n)]


def join_10_char(*itms, dp=3):
    """Joins a set of values with a 10 character buffer and right-justified"""
    string = ""
    for itm in itms:
        if itm is None:
            itm = ""
        if isinstance(itm, float):
            # save to 3 dp
            # Use scientific notation if number greater than NOTATION_THRESHOLD characters
            itm = f"{itm:.{dp}e}" if len(f"{itm:.{dp}f}") > NOTATION_THRESHOLD else f"{itm:.{dp}f}"
        itm = str(itm)
        itm = itm[:10]
        string += f"{itm:>10}"
    return string


def join_12_char_ljust(*itms, dp=3):
    """Joins a set of values with a 12 character buffer and left-justified"""
    return join_n_char_ljust(12, *itms, dp=dp)


def join_n_char_ljust(n, *itms, dp=3):
    """Joins a set of values with a n character buffer and left-justified"""
    string = ""
    for itm in itms:
        if itm is None:
            itm = ""
        if isinstance(itm, float):
            # save to 3 dp
            # Use scientific notation if number greater than 10 characters
            itm = f"{itm:.{dp}e}" if len(f"{itm:.{dp}f}") > NOTATION_THRESHOLD else f"{itm:.{dp}f}"
        itm = str(itm)
        itm = itm[:n]
        string += f"{itm:<{n}}"
    return string


def to_float(itm, default=0.0):
    try:
        return float(itm)
    except ValueError:
        return default


def to_int(itm, default=0):
    try:
        return int(itm)
    except ValueError:
        return default


def to_str(itm, default, check_float=False):
    if check_float:
        try:
            return float(itm)
        except ValueError:
            pass
    if itm == "":
        return default
    return itm


def to_data_list(block: list[str], num_cols: int | None = None, date_col: int | None = None):
    if num_cols is not None:
        num_cols += 1 if date_col is not None else 0
    data_list = []
    for row in block:
        row_split = split_10_char(row) if num_cols is None else split_10_char(row)[:num_cols]
        if date_col is not None:
            date_time = " ".join(row_split[date_col : date_col + 2])
            row_split = [
                to_float(itm)
                for idx, itm in enumerate(row_split)
                if idx not in (date_col, date_col + 1)
            ]
            row_split.insert(date_col, date_time)
        else:
            row_split = [to_float(itm) for itm in row_split]

        row_list = list(row_split)
        data_list.append(row_list)
    return data_list


def set_bridge_params(obj: Any, line: str, *, include_pier: bool = True) -> None:
    params = split_10_char(f"{line:<90}")
    obj.calibration_coefficient = to_float(params[0], 1.0)
    obj.skew = to_float(params[1])
    obj.bridge_width_dual = to_float(params[2])
    obj.bridge_dist_dual = to_float(params[3])
    if include_pier:
        obj.total_pier_width = to_float(params[4])
    obj.orifice_flow = params[5] == "ORIFICE"
    obj.orifice_lower_transition_dist = to_float(params[6])
    obj.orifice_upper_transition_dist = to_float(params[7])
    obj.orifice_discharge_coefficient = to_float(params[8], 1.0)


def set_pier_params(obj: Any, line: str) -> None:
    pier_info = split_10_char(line)
    if int(pier_info[0]) > 0:
        obj.specify_piers = True
        obj.npiers = int(pier_info[0])
        if pier_info[1] == "COEFF":
            obj.pier_use_calibration_coeff = True
            obj.pier_calibration_coeff = to_float(pier_info[3])
        else:
            obj.pier_use_calibration_coeff = False
            obj.pier_shape = pier_info[1]
            obj.pier_faces = pier_info[2]
    else:
        obj.specify_piers = False
        obj.soffit_shape = pier_info[1]


def read_dataframe_from_lines(
    all_lines: list[str],
    end_idx: int,
    read_lines: Callable[[list[str]], pd.DataFrame],
    *args,
    **kwargs,
) -> tuple[int, int, pd.DataFrame]:
    nrows = get_int(all_lines[end_idx])
    start_idx = end_idx + 1
    end_idx = start_idx + nrows
    data = read_lines(all_lines[start_idx:end_idx], *args, **kwargs)
    return nrows, end_idx, data


def read_bridge_cross_sections(
    lines: list[str],
    *,
    include_panel_marker: bool = False,
    include_top_level: bool = False,
) -> pd.DataFrame:
    data_list = []
    for line in lines:
        line_split = split_10_char(f"{line:<50}")
        df_row = [
            to_float(line_split[0]),
            to_float(line_split[1]),
            to_float(line_split[2]),
        ]

        if include_panel_marker:
            df_row.append(line_split[3])

        df_row.append(line_split[4])

        if include_top_level:
            df_row.append(line_split[5])

        data_list.append(df_row)

    columns = ["X", "Y", "Mannings n"]

    if include_panel_marker:
        columns.append("Panel")

    columns.append("Embankments")

    if include_top_level:
        columns.append("Top Level")
    return pd.DataFrame(data_list, columns=columns)


def read_bridge_opening_data(lines: list[str]) -> pd.DataFrame:
    data_list = []
    for line in lines:
        line_split = split_10_char(f"{line:<40}")
        start = to_float(line_split[0])
        finish = to_float(line_split[1])
        spring = to_float(line_split[2])
        soffit = to_float(line_split[3])
        data_list.append([start, finish, spring, soffit])
    return pd.DataFrame(data_list, columns=["Start", "Finish", "Springing Level", "Soffit Level"])


def read_bridge_culvert_data(lines: list[str]) -> pd.DataFrame:
    data_list = []
    for line in lines:
        line_split = split_10_char(f"{line:<70}")
        invert = to_float(line_split[0])
        soffit = to_float(line_split[1])
        area = to_float(line_split[2])
        cd_part = to_float(line_split[3])
        cd_full = to_float(line_split[4])
        dlinen = to_float(line_split[5])
        x = to_float(line_split[6])
        data_list.append([invert, soffit, area, cd_part, cd_full, dlinen, x])
    return pd.DataFrame(
        data_list,
        columns=[
            "Invert",
            "Soffit",
            "Section Area",
            "Cd Part Full",
            "Cd Full",
            "Drowning Coefficient",
            "X",
        ],
    )


def read_bridge_pier_locations(lines: list[str]) -> pd.DataFrame:
    data_list = []
    for line in lines:
        line_split = split_10_char(f"{line:<40}")
        l_x = to_float(line_split[0])
        l_top_level = to_float(line_split[1])
        r_x = to_float(line_split[2])
        r_top_level = to_float(line_split[3])
        data_list.append([l_x, l_top_level, r_x, r_top_level])
    return pd.DataFrame(
        data_list,
        columns=["Left X", "Left Top Level", "Right X", "Right Top Level"],
    )


def read_spill_section_data(lines: list[str]) -> pd.DataFrame:
    data_list = []
    for line in lines:
        line_split = split_10_char(f"{line:<40}")
        chainage = to_float(line_split[0])
        elevation = to_float(line_split[1])
        easting = to_float(line_split[2])
        northing = to_float(line_split[3])
        data_list.append([chainage, elevation, easting, northing])
    return pd.DataFrame(data_list, columns=["X", "Y", "Easting", "Northing"])


def read_superbridge_opening_data(lines: list[str]) -> pd.DataFrame:
    data_list = []
    for line in lines:
        line_split = split_10_char(f"{line:<20}")
        x = to_float(line_split[0])
        z = to_float(line_split[1])
        data_list.append([x, z])
    return pd.DataFrame(data_list, columns=["X", "Z"])


def read_superbridge_block_data(lines: list[str]) -> pd.DataFrame:
    data_list = []
    for line in lines:
        line_split = split_10_char(f"{line:<30}")
        percentage = to_int(line_split[0])
        time = to_float(line_split[1])
        datetime = to_float(line_split[2])
        data_list.append([percentage, time, datetime])
    return pd.DataFrame(data_list, columns=["percentage", "time", "datetime"])


def get_int(line: str) -> int:
    return int(float(split_10_char(line)[0]))


def write_dataframe(
    header: int | str | None,
    df: pd.DataFrame,
    empty: int | None = None,
) -> list[str]:
    df_to_use = copy.deepcopy(df)
    if empty is not None:
        df_to_use.insert(empty, "_", [None] * len(df_to_use))
    lines = [join_10_char(*x) for x in df_to_use.itertuples(index=False)]
    if header is not None:
        lines = [str(header), *lines]
    return lines


def write_dataframes(
    header: int | str | None,
    subheaders: list[int],
    df_list: list[pd.DataFrame],
) -> list[str]:
    list_of_lists = [write_dataframe(x, y) for x, y in zip(subheaders, df_list)]
    lines = list(chain.from_iterable(list_of_lists))
    if header is not None:
        lines = [str(header), *lines]
    return lines
