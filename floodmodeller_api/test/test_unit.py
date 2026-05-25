from __future__ import annotations

import pandas as pd
import pytest

from floodmodeller_api import units
from floodmodeller_api.units import QTBDY
from floodmodeller_api.units._base import Unit  # update this import path to match your repo


class DummyUnit(Unit):
    def __init__(self, unit_value: str):
        self._unit = unit_value


@pytest.mark.parametrize(
    ("unit", "header", "expected_revision", "expected_comment"),
    [
        ("RESERVOIR", "RESERVOIR 45678 This is a comment", None, "45678 This is a comment"),
        ("RESERVOIR", "RESERVOIR #revision#1 Mr Comment123", 1, "Mr Comment123"),
        ("LATERAL", "LATERAL #revision#1", 1, ""),
        ("RIVER", "RIVER look at this lovely RIVER", None, "look at this lovely RIVER"),
    ],
)
def test_get_revision_and_comment(
    unit: str,
    header: str,
    expected_revision: int | None,
    expected_comment: str,
):
    dummy_unit = DummyUnit(unit)
    revision, comment = dummy_unit._get_revision_and_comment(header)
    assert revision == expected_revision
    assert comment == expected_comment


@pytest.mark.parametrize(
    ("unit", "header", "remove_revision", "expected_result"),
    [
        ("RESERVOIR", "RESERVOIR 45678 This is a comment", True, "45678 This is a comment"),
        ("RESERVOIR", "RESERVOIR #revision#1 Mr Comment123", True, "Mr Comment123"),
        (
            "LATERAL",
            "LATERAL #revision#1 another #revision#1 tag",
            True,
            "another #revision#1 tag",
        ),
        (
            "LATERAL",
            "LATERAL #revision#1 another #revision#1 tag",
            False,
            "#revision#1 another #revision#1 tag",
        ),
        ("RIVER", "RIVER look at this lovely RIVER", False, "look at this lovely RIVER"),
    ],
)
def test_remove_unit_name(unit: str, header: str, remove_revision: bool, expected_result: str):
    dummy_unit = DummyUnit(unit)
    result = dummy_unit._remove_unit_name(header, remove_revision=remove_revision)
    assert result == expected_result


def test_partially_defined_unit():
    actual = QTBDY(["QTBDY comment", "test", "1", "0"]).data
    expected = pd.Series(
        [0],
        index=pd.Index([0], name="Time"),
        name="Flow",
    )
    pd.testing.assert_series_equal(expected, actual)


def test_create_unit_from_blank():
    """Test to create units with no parameters or subtype specified."""

    errors = {}
    for unit_type in units.SUPPORTED_UNIT_TYPES:
        if unit_type in ["INITIAL CONDITIONS", "VARIABLES"]:
            continue

        # Changes done to account for unit types with spaces/dashes eg Flat-V Weir
        unit_type_safe = unit_type.replace(" ", "_").replace("-", "_")

        # Get class object from unit type
        unit = getattr(units, unit_type_safe)

        try:
            # Create unit from blank and check the raw block can be written
            unit()._write()
        except NotImplementedError:
            pass
        except Exception as e:
            errors[unit_type] = e

    messages = ("\n" + "\n".join(
    f"{unit_type}: {error}"
    for unit_type, error in errors.items()
    ) + "\n")
    assert errors == {}, messages


def test_create_subtypes_from_blank():
    """Test to create units with subtype specified but no parameters specified."""

    # Units where the subtype is defined using the boolean argument "flapped"
    flapped_units = ["ORIFICE", "OUTFALL"]

    errors = {}
    for unit_type in units.SUPPORTED_UNIT_TYPES:

        if units.SUPPORTED_UNIT_TYPES[unit_type]["has_subtype"] is False:
            continue

        unit_type_safe = unit_type.replace(" ", "_").replace("-", "_")
        unit = getattr(units, unit_type_safe)

        # For units which are supported, check through all subtypes
        subtypes = units.SUPPORTED_UNIT_TYPES[unit_type]["subtypes"]
        for subtype in subtypes:
            try:
                if unit_type in flapped_units:
                    unit(flapped=subtype=="FLAPPED")._write()
                else:
                    unit(subtype=subtype)._write()

            except NotImplementedError:  # noqa: PERF203
                continue

            except Exception as e:
                errors[f"{unit_type} {subtype}"] = e

    messages = ("\n" + "\n".join(
    f"{unit_subtype}: {error}"
    for unit_subtype, error in errors.items()
    ) + "\n")
    assert errors == {}, messages
