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

from ._base import Unit
from ._helpers import split_n_char


class UNSUPPORTED(Unit):
    """Used to read in all unsupported unit types, simply returning the raw data on write"""

    def _read(self, block, unit_name, unit_type, subtype):
        self.name = unit_name
        self._unit = unit_type
        self._subtype = subtype
        self._raw_block = block
        self.comment = block[0].replace(self._unit, "").strip()

        if self._subtype is False:
            self.labels = split_n_char(f"{block[1]:<{2*self._label_len}}", self._label_len)

        else:
            self._subtype = block[1].split(" ")[0].strip()
            if self._unit == "JUNCTION":
                self.labels = split_n_char(block[2], self._label_len)
            self.labels = split_n_char(f"{block[2]:<{2*self._label_len}}", self._label_len)

        if self.labels[1] != "" and self._unit != "JUNCTION":
            self.ds_label = self.labels[1]

    def _write(self):
        return self._raw_block
