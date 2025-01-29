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

""" Holds the base unit class for all FM Units """

import logging

import pandas as pd

from ..diff import check_item_with_dataframe_equal
from ..to_from_json import Jsonable
from ._helpers import join_10_char, join_n_char_ljust, split_10_char, to_float, to_str


class Unit(Jsonable):
    _unit: str
    _subtype: str | None = None
    _name: str | None = None

    def __init__(self, unit_block=None, n=12, from_json: bool = False, **kwargs):
        if from_json:
            return
        self._label_len = n
        if unit_block is not None:
            self._read(unit_block, **kwargs)
        else:
            self._create_from_blank(**kwargs)

    @property
    def unit(self) -> str:
        return self._unit

    @property
    def name(self) -> str | None:
        return self._name

    @name.setter
    def name(self, new_name):
        try:
            new_name = str(new_name)
            if " " in new_name:
                msg = f'Cannot set unit name to "{new_name}" as it contains one or more spaces'
                raise Exception(msg)
            self._name = new_name
        except Exception as e:
            msg = f'Failed to set unit name to "{new_name}" due to error: {e}'
            raise Exception(msg) from e

    @property
    def subtype(self) -> str | None:
        return self._subtype

    @subtype.setter
    def subtype(self, new_value):
        msg = "You cannot change the subtype of a unit once it has been instantiated"
        raise ValueError(msg)

    def __repr__(self):
        if self._subtype is None:
            return f"<floodmodeller_api Unit Class: {self._unit}(name={self._name})>"
        return (
            f"<floodmodeller_api Unit Class: {self._unit}(name={self._name}, type={self._subtype})>"
        )

    def _create_from_blank(self):
        msg = f"Creating new {self._unit} units is not yet supported by floodmodeller_api, only existing units can be read"
        raise NotImplementedError(msg)

    def __str__(self):
        return "\n".join(self._write())

    def _read(self, block: list[str]):
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

    # rules & varrules

    def _read_rules(self, block):
        rule_params = split_10_char(block[self._last_gate_row + 1])
        self.nrules = int(rule_params[0])
        self.rule_sample_time = to_float(rule_params[1])
        self.timeunit = to_str(rule_params[2], "SECONDS", check_float=False)
        self.extendmethod = to_str(rule_params[3], "EXTEND")
        self.rules = self._get_logical_rules(self.nrules, block, self._last_gate_row + 2)
        # Get time rule data set
        nrows = int(split_10_char(block[self._last_rule_row + 1])[0])
        data_list = []
        for row in block[self._last_rule_row + 2 : self._last_rule_row + 2 + nrows]:
            row_split = split_10_char(f"{row:<20}")
            x = to_float(row_split[0])  # time
            y = row[10:].strip()  # operating rules
            data_list.append([x, y])
        self._last_time_row = self._last_rule_row + nrows + 1
        rule_data = pd.DataFrame(data_list, columns=["Time", "Operating Rules"])
        rule_data = rule_data.set_index("Time")
        rule_data = rule_data["Operating Rules"]
        self.time_rule_data = rule_data
        # VARRULES (not always necessary)
        self.has_varrules = False
        if (self._last_time_row + 1 < len(block)) and (
            block[self._last_time_row + 1].strip() == "VARRULES"
        ):
            self.has_varrules = True
            varrule_params = split_10_char(block[self._last_time_row + 2])
            self.nvarrules = int(varrule_params[0])
            self.varrule_sample_time = to_float(rule_params[1])
            self.varrules = self._get_logical_rules(self.nvarrules, block, self._last_time_row + 3)
            # Get time rule data set
            var_nrows = int(split_10_char(block[self._last_rule_row + 1])[0])
            data_list = []
            for row in block[self._last_rule_row + 2 : self._last_rule_row + 2 + var_nrows]:
                row_split = split_10_char(f"{row:<20}")
                x = to_float(row_split[0])  # time
                y = row[10:].strip()  # operating rules
                data_list.append([x, y])

            varrule_data = pd.DataFrame(data_list, columns=["Time", "Operating Rules"])
            varrule_data = varrule_data.set_index("Time")
            varrule_data = varrule_data["Operating Rules"]
            self.time_varrule_data = varrule_data

    def _write_rules(self, block):
        # ADD RULES
        block.append("RULES")
        self.nrules = len(self.rules)
        block.append(
            f"{join_n_char_ljust(10, self.nrules)}{join_10_char(self.rule_sample_time)}{join_n_char_ljust(10, self.timeunit, self.extendmethod)}",
        )
        for rule in self.rules:
            block.append(rule["name"])
            block.extend(rule["logic"].split("\n"))

        # ADD TIME RULE DATA SET
        block.append("TIME RULE DATA SET")
        block.append(join_10_char(len(self.time_rule_data)))
        time_rule_data = [f"{join_10_char(t)}{o_r:<10}" for t, o_r in self.time_rule_data.items()]
        block.extend(time_rule_data)

        # ADD VARRULES (IF THEY ARE THERE)
        if self.has_varrules:
            block.append("VARRULES")
            self.nvarrules = len(self.varrules)
            block.append(
                f"{join_n_char_ljust(10, self.nvarrules)}{join_10_char(self.varrule_sample_time)}{join_n_char_ljust(10, self.timeunit, self.extendmethod)}",
            )
            for varrule in self.varrules:
                block.append(varrule["name"])
                block.extend(varrule["logic"].split("\n"))

            # ADD TIME VARRULE DATA SET
            block.append("TIME RULE DATA SET")
            block.append(join_10_char(len(self.time_varrule_data)))
            time_varrule_data = [
                f"{join_10_char(t)}{o_r:<10}" for t, o_r in self.time_rule_data.items()
            ]
            block.extend(time_varrule_data)

        return block

    def _get_logical_rules(self, nrules, block, rule_row):
        rules = []
        rules_recorded = 0
        rule_logic = []
        rule_dict = {}
        nl = "\n"
        while rules_recorded < nrules:
            if block[rule_row].strip().upper().endswith(("END", "ENDIF")):
                rule_logic.append(block[rule_row])
                rule_dict["logic"] = f"{nl.join(rule_logic)}"
                rules.append(rule_dict)
                rule_logic = []
                rule_dict = {}
                rules_recorded += 1
            elif len(rule_dict) == 0:
                rule_dict = {"name": block[rule_row].strip()}
            else:
                rule_logic.append(block[rule_row])
            rule_row += 1

        self._last_rule_row = rule_row

        return rules
