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

from .parameters import parameter_options
from .urban_parameters import urban_parameter_options


def _validate_unit(unit, urban=False):
    """Validate parameters are the correct type for the unit"""
    param_validation_dict = {}
    all_valid = True
    for param in dir(unit):
        # define which dictionary to use
        options = parameter_options if not urban else urban_parameter_options

        if param in options:
            value = getattr(unit, param)
            param_validation_dict[param] = _validate_parameter(options[param], value)
            if not param_validation_dict[param][0]:
                all_valid = False

    if not all_valid:
        errors = ",\n     ".join(
            [
                f"{param} {value[1]}"
                for param, value in param_validation_dict.items()
                if not value[0]
            ],
        )
        msg = f"One or more parameters in {unit!r} are invalid:\n     {errors}"
        raise ValueError(msg)


def _validate_parameter(param, value):  # noqa: C901, PLR0911, PLR0912
    if param["type"] == "type-match":
        return isinstance(value, param["options"]), f'-> Expected: {param["options"]}'

    if param["type"] == "value-match":
        if isinstance(value, str):
            return value.upper() in param["options"], f'-> Expected: {param["options"]}'
        return value in param["options"], f'-> Expected: {param["options"]}'

    if param["type"] == "end-value-match":
        if value.strip().upper().endswith(tuple(param["options"])):
            return (True, 0)
        return (
            False,
            f"-> Could not add rule: \n{value}\n     as it doesn't end with END or ENDIF.",
        )

    if param["type"] == "type-value-match":
        new_rule = {"type": "type-match", "options": param["options"][0]}
        type_match_result = _validate_parameter(new_rule, value)[0]

        new_rule = {"type": "value-match", "options": param["options"][1]}
        value_match_result = _validate_parameter(new_rule, value)[0]

        return (
            type_match_result or value_match_result,
            f'-> Expected: Type {param["options"][0]} or Value {param["options"][1]}',
        )

    if param["type"] == "value-range":
        lower = param["options"][0]
        upper = param["options"][1]
        try:
            return lower <= value <= upper, f"-> Out of valid range: {lower} - {upper}"
        except TypeError:
            return False, f"-> Out of valid range: {lower} - {upper}"

    if param["type"] == "string-length":
        return (
            len(value) <= param["max_length"],
            f'-> Exceeds {param["max_length"]} characters',
        )

    if param["type"] == "list-string-length":
        return (
            all(len(item) <= param["max_length"] for item in value),
            f'-> Contains labels exceeding {param["max_length"]} characters',
        )

    if param["type"] == "dict-match":
        for key, rule in param["options"].items():
            if key not in value:
                return False, f"-> Missing required dict key: {key}"
            if not _validate_parameter(rule, value[key])[0]:
                return _validate_parameter(rule, value[key])
        return True, 0

    if param["type"] == "list-dict-match":
        for item in value:
            for key, rule in param["options"].items():
                if key not in item:
                    return (
                        False,
                        f"-> One or more items missing required dict key: {key}",
                    )
                if not _validate_parameter(rule, item[key])[0]:
                    return _validate_parameter(rule, item[key])
        return True, 0

    return None
