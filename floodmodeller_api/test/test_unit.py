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
