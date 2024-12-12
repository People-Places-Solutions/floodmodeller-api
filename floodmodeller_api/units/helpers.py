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

from __future__ import annotations

import pandas as pd

NOTATION_THRESHOLD = 10


def split_10_char(line):
    return [line[i : i + 10].strip() for i in range(0, len(line), 10)]


def split_12_char(line):
    return [line[i : i + 12].strip() for i in range(0, len(line), 12)]


def split_n_char(line, n):
    return [line[i : i + n].strip() for i in range(0, len(line), n)]


def join_10_char(*itms, dp=3):
    """Joins a set of values with a 10 character buffer and right-justified"""
    string = ""
    for itm in itms:
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
    string = ""
    for itm in itms:
        if isinstance(itm, float):
            # save to 3 dp
            # Use scientific notation if number greater than 10 characters
            itm = f"{itm:.{dp}e}" if len(f"{itm:.{dp}f}") > NOTATION_THRESHOLD else f"{itm:.{dp}f}"
        itm = str(itm)
        itm = itm[:12]
        string += f"{itm:<12}"
    return string


def join_n_char_ljust(n, *itms, dp=3):
    """Joins a set of values with a n character buffer and left-justified"""
    string = ""
    for itm in itms:
        if isinstance(itm, float):
            # save to 3 dp
            # Use scientific notation if number greater than 10 characters
            itm = f"{itm:.{dp}e}" if len(f"{itm:.{dp}f}") > NOTATION_THRESHOLD else f"{itm:.{dp}f}"
        itm = str(itm)
        itm = itm[:n]
        string += f"{itm:<{n}}"
    return string


def _to_float(itm, default=0.0):
    try:
        return float(itm)
    except ValueError:
        return default


def _to_int(itm, default=0):
    try:
        return int(itm)
    except ValueError:
        return default


def _to_str(itm, default, check_float=False):
    if check_float:
        try:
            return float(itm)
        except ValueError:
            pass
    if itm == "":
        return default
    return itm


def _to_data_list(block: list[str], num_cols: int | None = None, date_col: int | None = None):
    if num_cols is not None:
        num_cols += 1 if date_col is not None else 0
    data_list = []
    for row in block:
        row_split = split_10_char(row) if num_cols is None else split_10_char(row)[:num_cols]
        if date_col is not None:
            date_time = " ".join(row_split[date_col : date_col + 2])
            row_split = [
                _to_float(itm)
                for idx, itm in enumerate(row_split)
                if idx not in (date_col, date_col + 1)
            ]
            row_split.insert(date_col, date_time)
        else:
            row_split = [_to_float(itm) for itm in row_split]

        row_list = list(row_split)
        data_list.append(row_list)
    return data_list


def read_bridge_params(line: str) -> dict[str, str | bool]:
    params = split_10_char(f"{line:<90}")
    return {
        "calibration_coefficient": _to_float(params[0], 1.0),
        "skew": _to_float(params[1]),
        "bridge_width_dual": _to_float(params[2]),
        "bridge_dist_dual": _to_float(params[3]),
        "total_pier_width": _to_float(params[4]),
        "orifice_flow": params[5] == "ORIFICE",
        "orifice_lower_transition_dist": _to_float(params[6]),
        "orifice_upper_transition_dist": _to_float(params[7]),
        "orifice_discharge_coefficient": _to_float(params[8], 1.0),
    }


def read_bridge_cross_sections(lines: list[str], include_top_level: bool = False) -> pd.DataFrame:
    data_list = []
    for line in lines:

        line_split = split_10_char(f"{line:<50}")
        df_row = [
            _to_float(line_split[0]),
            _to_float(line_split[1]),
            _to_float(line_split[2]),
            line_split[4],
        ]

        if include_top_level:
            df_row.append(line_split[5])

        data_list.append(df_row)

    columns = ["X", "Y", "Mannings n", "Embankments"]
    if include_top_level:
        columns.append("Top Level")
    return pd.DataFrame(data_list, columns=columns)


def read_bridge_opening_data(lines: list[str]) -> pd.DataFrame:
    data_list = []
    for line in lines:
        line_split = split_10_char(f"{line:<40}")
        start = _to_float(line_split[0])
        finish = _to_float(line_split[1])
        spring = _to_float(line_split[2])
        soffit = _to_float(line_split[3])
        data_list.append([start, finish, spring, soffit])
    return pd.DataFrame(data_list, columns=["Start", "Finish", "Springing Level", "Soffit Level"])


def read_bridge_culvert_data(lines: list[str]) -> pd.DataFrame:
    data_list = []
    for line in lines:
        line_split = split_10_char(f"{line:<60}")
        invert = _to_float(line_split[0])
        soffit = _to_float(line_split[1])
        area = _to_float(line_split[2])
        cd_part = _to_float(line_split[3])
        cd_full = _to_float(line_split[4])
        dlinen = _to_float(line_split[5])
        data_list.append([invert, soffit, area, cd_part, cd_full, dlinen])
    return pd.DataFrame(
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


def read_bridge_pier_locations(lines: list[str]) -> pd.DataFrame:
    data_list = []
    for line in lines:
        line_split = split_10_char(f"{line:<40}")
        l_x = _to_float(line_split[0])
        l_top_level = _to_float(line_split[1])
        r_x = _to_float(line_split[2])
        r_top_level = _to_float(line_split[3])
        data_list.append([l_x, l_top_level, r_x, r_top_level])
    return pd.DataFrame(
        data_list,
        columns=["Left X", "Left Top Level", "Right X", "Right Top Level"],
    )


def read_spill_section_data(lines: list[str]) -> pd.DataFrame:
    data_list = []
    for line in lines:
        line_split = split_10_char(f"{line:<40}")
        chainage = _to_float(line_split[0])
        elevation = _to_float(line_split[1])
        easting = _to_float(line_split[2])
        northing = _to_float(line_split[3])
        data_list.append([chainage, elevation, easting, northing])
    return pd.DataFrame(data_list, columns=["X", "Y", "Easting", "Northing"])


def read_superbridge_opening_data(lines: list[str]) -> pd.DataFrame:
    data_list = []
    for line in lines:
        line_split = split_10_char(f"{line:<20}")
        x = _to_float(line_split[0])
        z = _to_float(line_split[1])
        data_list.append([x, z])
    return pd.DataFrame(data_list, columns=["X", "Z"])


def read_superbridge_block_data(lines: list[str]) -> pd.DataFrame:
    data_list = []
    for line in lines:
        line_split = split_10_char(f"{line:<30}")
        percentage = _to_int(line_split[0])
        time = _to_float(line_split[1])
        datetime = _to_float(line_split[2])
        data_list.append([percentage, time, datetime])
    return pd.DataFrame(data_list, columns=["percentage", "time", "datetime"])


def get_int(line: str) -> int:
    return int(split_10_char(line)[0])
