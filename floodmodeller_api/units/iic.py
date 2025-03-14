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

from ..diff import check_item_with_dataframe_equal
from ..to_from_json import Jsonable
from ._helpers import join_10_char, split_10_char

# Initial Conditions Class


class IIC(Jsonable):
    """Class to hold initial conditions data"""

    def __init__(self, ic_block=None, n=12, from_json: bool = False):
        if from_json:
            return
        self._label_len = n
        self._read(ic_block)

    def __repr__(self):
        return "<floodmodeller_api Initial Conditions Class: IIC()>"

    def _read(self, ic_block):
        header = [
            "label",
            "?",
            "flow",
            "stage",
            "froude no",
            "velocity",
            "umode",
            "ustate",
            "z",
        ]
        data_list = []
        for line in ic_block[2:]:
            lbl = line[: self._label_len + 1].strip()
            incl = line[self._label_len + 1 : self._label_len + 3].strip()
            q, h, fr, v, um, us, z = split_10_char(line[self._label_len + 3 :])
            data_list.append(
                [
                    lbl,
                    incl,
                    float(q),
                    float(h),
                    float(fr),
                    float(v),
                    float(um),
                    float(us),
                    float(z),
                ],
            )
        self.data = pd.DataFrame(data_list, columns=header)

    def _write(self):
        ic_block = [
            "INITIAL CONDITIONS",
            " label   ?      flow     stage froude no  velocity     umode    ustate         z",
        ]
        rows = []
        for _, lbl, incl, q, h, fr, v, um, us, z in self.data.itertuples():
            string = f"{lbl:<{self._label_len}}{incl:>2}"
            string += join_10_char(q, h, fr, v, um, us, z)
            rows.append(string)

        ic_block.extend(rows)

        return ic_block

    def update_label(self, old, new):
        self.data.loc[self.data["label"] == old, "label"] = new

    def _get_diff(self, other):
        return self.__eq__(other, return_diff=True)  # pylint: disable=unnecessary-dunder-call

    def __eq__(self, other, return_diff=False):
        result = True
        diff = []
        result, diff = check_item_with_dataframe_equal(
            self.__dict__,
            other.__dict__,
            name="Initial Conditions",
            diff=diff,
        )
        return (result, diff) if return_diff else result
