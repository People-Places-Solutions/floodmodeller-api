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

# Helper Functions
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
