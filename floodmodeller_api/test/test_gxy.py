from __future__ import annotations

from pathlib import Path

import pytest

from floodmodeller_api import DAT
from floodmodeller_api.units import (
    FLOODPLAIN,
    INTERPOLATE,
    QTBDY,
    REPLICATE,
    RESERVOIR,
    RIVER,
    SPILL,
)


# this would be a fixture but doesnt work when used in parameterised test.
def blank_with_location(unit_class, *args, **kwargs):
    unit = unit_class(*args, **kwargs)
    unit._location = (461193.10, 339088.74)
    return unit


@pytest.mark.parametrize(
    ("unit", "expected_outcome"),
    [
        (RIVER(), None),
        (QTBDY(), None),
        (INTERPOLATE(), None),
        (INTERPOLATE(easting=123.4, northing=987.6), (123.4, 987.6)),
        (REPLICATE(), None),
        (REPLICATE(easting=123.4, northing=987.6), (123.4, 987.6)),
        (RESERVOIR(), None),
        (RESERVOIR(easting=123.4, northing=987.6), (123.4, 987.6)),
        (SPILL(), None),
        (FLOODPLAIN(), None),
        (blank_with_location(QTBDY), (461193.10, 339088.74)),
        (blank_with_location(RIVER), (461193.10, 339088.74)),
        (blank_with_location(INTERPOLATE), (461193.10, 339088.74)),
        (blank_with_location(INTERPOLATE, easting=123.4, northing=987.6), (461193.10, 339088.74)),
        (blank_with_location(SPILL), (461193.10, 339088.74)),
        (blank_with_location(FLOODPLAIN), (461193.10, 339088.74)),
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


@pytest.mark.parametrize(
    ("dat_name", "group", "label", "expected_outcome"),
    [
        ("EX1.DAT", "sections", "S4", (-38203.94169253, 153846.153846154)),
        ("River_Bridge_no_gxy.dat", "sections", "M029", (385029.200, 242717.100)),
        ("River_Bridge_no_gxy.dat", "sections", "M030", (384689.300, 242345.700)),
        ("River_Bridge_no_gxy.dat", "sections", "M031", (384545.000, 241937.000)),
        ("River_Bridge_no_gxy.dat","structures","M047spU",(386710.9, 236857.85)),
    ],
)
def test_unit_from_dat(test_workspace, dat_name, group, label, expected_outcome):
    dat_path = Path(test_workspace, dat_name)
    dat = DAT(dat_path)
    unit = getattr(dat, group)[label]
    assert unit.location == expected_outcome
