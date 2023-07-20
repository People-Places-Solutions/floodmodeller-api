"""
Flood Modeller Python API
Copyright (C) 2023 Jacobs U.K. Limited

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty 
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details. 

You should have received a copy of the GNU General Public License along with this program.  If not, see https://www.gnu.org/licenses/.

If you have any query about this program or this License, please contact us at support@floodmodeller.com or write to the following 
address: Jacobs UK Limited, Flood Modeller, Cottons Centre, Cottons Lane, London, SE1 2QG, United Kingdom.
"""

import pandas as pd

from .helpers import join_10_char, join_n_char_ljust
from ..diff import check_item_with_dataframe_equal

### Variables, Rules & Varrules Classes ###


class Variables:
    """Class to hold VARIABLES"""

    def __init__(self, var_block):
        self._read(var_block)

    def __repr__(self):
        return f"<floodmodeller_api Variables Class: Variables()>"

    def _read(self, var_block):
        header = [
            "name",
            "type",
            "initial value",
            "initial status",
        ]
        data_list = []
        for line in var_block[1:-1]:
            name = line[:20].strip()
            type = line[20:30].strip()
            initial_value = line[30:40].strip()
            if type.upper() == "TIMER":
                initial_status = line[40:50].strip()
            else:
                initial_status = "n/a"  # unless the type is a timer, nothing else has an initial status
            data_list.append(
                [
                    name,
                    type,
                    initial_value,
                    initial_status,
                ]
            )
        self.data = pd.DataFrame(data_list, columns=header)

    def _write(self):
        var_block = [
            "VARIABLES",
        ]
        rows = []
        for _, nme, typ, iva, ist in self.data.itertuples():
            string = f"{nme:<{20}}"
            if typ == "timer":
                string += join_10_char(typ, iva, ist)
            else:
                string += join_10_char(typ, iva)
            rows.append(string)

        var_block.extend(rows)
        var_block.append("END VARIABLES")

        return var_block

    def _get_diff(self, other):
        return self.__eq__(other, return_diff=True)

    def __eq__(self, other, return_diff=False):
        result = True
        diff = []
        result, diff = check_item_with_dataframe_equal(
            self.__dict__, other.__dict__, name=f"Variables", diff=diff
        )
        return (result, diff) if return_diff else result
