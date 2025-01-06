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

import pandas as pd


def check_item_with_dataframe_equal(  # noqa: C901, PLR0912
    item_a,
    item_b,
    name,
    diff,
    special_types=(),
):
    result = True
    try:
        if isinstance(item_a, dict):
            result, diff = check_dict_with_dataframe_equal(
                item_a,
                item_b,
                name,
                diff,
                special_types,
            )
        elif isinstance(item_a, list):
            result, diff = check_list_with_dataframe_equal(
                item_a,
                item_b,
                name,
                diff,
                special_types,
            )
        elif isinstance(item_a, (pd.DataFrame, pd.Series)):
            if isinstance(item_a.index, pd.RangeIndex):
                item_a.index = item_a.index.astype("int")
            if isinstance(item_b.index, pd.RangeIndex):
                item_b.index = item_b.index.astype("int")
            if not item_a.equals(item_b) and len(item_a) + len(item_b) != 0:
                result = False
                if isinstance(item_a, pd.Series):
                    item_a = pd.DataFrame(item_a).reset_index()
                    item_b = pd.DataFrame(item_b).reset_index()

                df_diff = pd.concat([item_a, item_b]).drop_duplicates(keep=False)
                rows = df_diff.index.unique().to_list()
                msg = f"{len(rows)} row(s) not equal:\n"
                row_diffs = []
                for row in rows:
                    for col in df_diff.columns:
                        if True not in df_diff.loc[row, col].duplicated().to_numpy():
                            vals = df_diff.loc[row, col].to_numpy()
                            row_diffs.append(
                                f"    Row: {row}, Col: '{col}' - left: {vals[0]}, right: {vals[1]}",
                            )
                msg += "\n".join(row_diffs)
                diff.append((name, msg))
        elif isinstance(item_a, special_types):
            # item is a Unit or other fmapi class
            result, new_diff = item_a._get_diff(item_b)
            new_diff = [(f"{name}->{new_name}", new_item) for new_name, new_item in new_diff]
            diff.extend(new_diff)
        elif item_a != item_b:
            result = False
            diff.append((name, f"{item_a} != {item_b}"))
    except Exception as e:
        result = False
        diff.append((name, f"Error encountered when comparing: {e.args[0]}"))

    return result, diff


def check_dict_with_dataframe_equal(dict_a, dict_b, name, diff, special_types):
    """Used to recursively check equivalence where there may be dataframe objects"""
    result = True
    try:
        for key, item in dict_a.items():
            try:
                _result, diff = check_item_with_dataframe_equal(
                    item,
                    dict_b[key],
                    name=f"{name}->{key}",
                    diff=diff,
                    special_types=special_types,
                )
                if not _result:
                    result = False
            except KeyError as ke:  # noqa: PERF203
                result = False
                diff.append((name, f"Key: '{ke.args[0]}' missing in other"))
                continue

        for key in dict_b:
            if key not in dict_a:
                result = False
                diff.append((name, f"Key: {key} missing from first object"))
    except Exception:
        result = False
        diff.append((name, "Error encountered when comparing"))

    return result, diff


def check_list_with_dataframe_equal(list_a, list_b, name, diff, special_types):
    result = True
    try:
        for idx, item in enumerate(list_a):
            _result, diff = check_item_with_dataframe_equal(
                item,
                list_b[idx],
                name=f"{name}->itm[{idx}]",
                diff=diff,
                special_types=special_types,
            )
            if not _result:
                result = False

        if len(list_a) != len(list_b):
            result = False
            diff.append((name, "Mismatch in list length"))
    except Exception:
        result = False
        diff.append((name, "Error encountered when comparing"))

    return result, diff
