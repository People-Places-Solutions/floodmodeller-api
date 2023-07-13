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
            nme = line[:20].strip()
            typ = line[20:30].strip()
            iva = line[30:40].strip()
            if typ == "timer":
                ist = line[40:50].strip()
            else:
                ist = "n/a"  # unless the type is a timer, nothing else has an initial status
            data_list.append(
                [
                    nme,
                    typ,
                    iva,
                    ist,
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


class Rules:
    """Class to hold RULES"""

    def __init__(self, var_block):
        self._read(var_block)

    def __repr__(self):
        return f"<floodmodeller_api Variables Class: Rules()>"

    def _read(self, rul_block):
        self.data = rul_block  # like this until we know how rules block works

    def _write(self):
        rul_block = self.data
        return rul_block
