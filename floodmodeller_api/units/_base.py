"""
Flood Modeller Python API
Copyright (C) 2022 Jacobs U.K. Limited

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty 
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details. 

You should have received a copy of the GNU General Public License along with this program.  If not, see https://www.gnu.org/licenses/.

If you have any query about this program or this License, please contact us at support@floodmodeller.com or write to the following 
address: Jacobs UK Limited, Flood Modeller, Cottons Centre, Cottons Lane, London, SE1 2QG, United Kingdom.
"""

""" Holds the base unit class for all FM Units """

from ..diff import check_item_with_dataframe_equal


class Unit:
    _unit = None
    _subtype = None
    _name = None

    def __init__(self, unit_block=None, n=12, **kwargs):
        self._label_len = n
        if unit_block != None:
            self._read(unit_block)
        else:
            self._create_from_blank(**kwargs)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        try:
            new_name = str(new_name)
            if " " in new_name:
                raise Exception(
                    f'Cannot set unit name to "{new_name}" as it contains one or more spaces'
                )
            self._name = new_name
        except Exception as e:
            raise Exception(
                f'Failed to set unit name to "{new_name}" due to error: {e}'
            )

    @property
    def subtype(self):
        return self._subtype

    @subtype.setter
    def subtype(self, new_value):
        raise ValueError(
            "You cannot changed the subtype of a unit once it has been instantiated"
        )

    def __repr__(self):
        if self._subtype is None:
            return f"<floodmodeller_api Unit Class: {self._unit}(name={self._name})>"
        else:
            return f"<floodmodeller_api Unit Class: {self._unit}(name={self._name}, type={self._subtype})>"

    def _create_from_blank(self):
        raise NotImplementedError(
            f"Creating new {self._unit} units is not yet supported by floodmodeller_api, only existing units can be read"
        )

    def __str__(self):
        return "\n".join(self._write())

    def _read(self):
        raise NotImplementedError

    def _write(self):
        raise NotImplementedError

    def _diff(self, other):
        diff = self._get_diff(other)
        if diff[0]:
            print("No difference, units are equivalent")
        else:
            print("\n".join([f"{name}:  {reason}" for name, reason in diff[1]]))

    def _get_diff(self, other):
        return self.__eq__(other, return_diff=True)

    def __eq__(self, other, return_diff=False):
        result = True
        diff = []
        result, diff = check_item_with_dataframe_equal(
            self.__dict__,
            other.__dict__,
            name=f"{self._unit}.{self._subtype or ''}.{self._name}",
            diff=diff,
        )
        return (result, diff) if return_diff else result
