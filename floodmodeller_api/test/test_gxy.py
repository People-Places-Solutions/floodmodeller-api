from __future__ import annotations

import pytest

from floodmodeller_api.units import QTBDY, RIVER


# this would be a fixture but doesnt work when used in parameterised test.
def blank_with_location():
    unit = QTBDY()
    unit._location = (461193.10, 339088.74)
    return unit


@pytest.mark.parametrize(
    ("unit", "expected_outcome"),
    [
        (RIVER(), None),
        (QTBDY(), None),
        (blank_with_location(), (461193.10, 339088.74)),
    ],
)
def test_unit_location(unit, expected_outcome):
    assert unit.location == expected_outcome


def test_setting_location():
    # first check that we get the not implemented error, then check that the location is still unaffected.
    # this test should be updated when location is read/write.
    unit = RIVER()
    with pytest.raises(NotImplementedError):
        unit.location = (461382.54, 339188.26)

    assert unit.location is None
    assert unit._location is None
