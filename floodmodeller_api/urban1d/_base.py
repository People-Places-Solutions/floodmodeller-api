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

""" Holds the base unit class for all FM 1D units Units """

import logging

from ..diff import check_item_with_dataframe_equal
from ..to_from_json import Jsonable


class UrbanUnit(Jsonable):
    _unit: str | None = None
    _subtype: str | None = None
    _name: str | None = None

    def __init__(self, unit_block=None, from_json: bool = False, **kwargs):
        if from_json:
            return
        if unit_block is not None:
            self._read(unit_block)
        else:
            self._create_from_blank(**kwargs)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name

    # Update this bit
    def __repr__(self):
        if self._subtype is None:
            return f"<floodmodeller_api UrbanUnit Class: {self._unit}(name={self._name})>"
        return None

    def _create_from_blank(self):
        msg = f"Creating new {self._unit} units is not yet supported by floodmodeller_api, only existing units can be read"
        raise NotImplementedError(msg)

    def __str__(self):
        return self._write()

    def _read(self, unit_block):
        raise NotImplementedError

    def _write(self):
        raise NotImplementedError

    def _diff(self, other):
        diff = self._get_diff(other)
        if diff[0]:
            logging.info("No difference, units are equivalent")
        else:
            logging.info("\n".join([f"{name}:  {reason}" for name, reason in diff[1]]))

    def _get_diff(self, other):
        return self.__eq__(other, return_diff=True)  # pylint: disable=unnecessary-dunder-call

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


class UrbanSubsection(Jsonable):
    _name: str | None = None
    _urban_unit_class: type[UrbanUnit] | None = None

    def __init__(self, subsection_block=None, from_json: bool = False, **kwargs):
        if from_json:
            return
        if subsection_block is not None:
            self._read(subsection_block)
        else:
            self._create_from_blank(**kwargs)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name

    def __repr__(self):
        return f"<floodmodeller_api UrbanSubsection Class: {self._attribute}>"

    def _create_from_blank(self):
        msg = f"Creating new {self._name} subsections is not yet supported by floodmodeller_api, only existing subsections can be read"
        raise NotImplementedError(msg)

    def __str__(self):
        return "\n".join(self._write())

    def _read(self, block):
        setattr(self, self._attribute, {})
        units = getattr(self, self._attribute)

        self._struct = []

        for line in block[1:]:  # first line is subsection name
            if line.strip() != "" and not line.startswith(";"):
                unit = self._urban_unit_class(line)
                units[unit.name] = unit
                self._struct.append(unit)

            else:
                self._struct.append(line)

    def _write(self):
        block = []

        if self._attribute == "raingauges":
            # handle required miss-spelling of raingauge in subsection header
            block.append("[" + "RAINGAGES" + "]")

        else:
            block.append("[" + self._attribute.upper() + "]")

        for line in self._struct:
            if isinstance(line, self._urban_unit_class):
                block.append(line._write())
            else:
                block.append(line)

        units = getattr(self, self._attribute)

        for name, unit in units.copy().items():
            if name != unit.name:
                # Miss-match found
                # check that it is not an existing label in units
                if unit.name in units:
                    msg = f'Error: Cannot update label "{name}" to "{unit.name}" beacuase "{unit.name}" already exists in the {self._attribute} subsection'
                    raise Exception(msg)

                units[unit.name] = unit
                del units[name]

        return block

    def _diff(self, other):
        diff = self._get_diff(other)
        if diff[0]:
            logging.info("No difference, units are equivalent")
        else:
            logging.info("\n".join([f"{name}:  {reason}" for name, reason in diff[1]]))

    def _get_diff(self, other):
        return self.__eq__(other, return_diff=True)  # pylint: disable=unnecessary-dunder-call

    def __eq__(self, other, return_diff=False):
        result = True
        diff = []
        result, diff = check_item_with_dataframe_equal(
            self.__dict__,
            other.__dict__,
            name=f"{self._attribute.upper()}",
            diff=diff,
        )
        return (result, diff) if return_diff else result
