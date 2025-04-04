from __future__ import annotations

import pytest

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
