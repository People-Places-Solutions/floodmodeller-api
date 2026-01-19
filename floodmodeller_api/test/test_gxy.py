from __future__ import annotations

from pathlib import Path

import pytest

import floodmodeller_api.units
from floodmodeller_api import DAT
from floodmodeller_api.units import (
    FLOODPLAIN,
    INTERPOLATE,
    JUNCTION,
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


def get_supported_unit_classes():
    all_unit_classes = []
    for unit_type, attributes in floodmodeller_api.units.SUPPORTED_UNIT_TYPES.items():
        if attributes["group"] not in ("other", "comments"):
            unit_type_safe = unit_type.replace(" ", "_").replace("-", "_")
            # Borrowed replacing idea from .dat
            unit_class = getattr(floodmodeller_api.units, unit_type_safe)
            all_unit_classes.append(unit_class)
    return all_unit_classes


SUPPORTED_UNIT_CLASSES = get_supported_unit_classes()


@pytest.mark.parametrize("unit_class", SUPPORTED_UNIT_CLASSES)
def test_setting_location(unit_class):
    # first check that we get the not implemented error, then check that the location is still unaffected.
    # this test should be updated when location is read/write capable.
    try:
        # Junction units cannot be created from blank without at least one label.
        unit = unit_class(labels=["label1"]) if unit_class == JUNCTION else unit_class()
    except NotImplementedError as error:
        pytest.skip(f"Creating unit {unit_class=} from blank not supported, skipping...\n{error=}")

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
        ("River_Bridge_no_gxy.dat", "structures", "M047spU", (386710.9, 236857.85)),
    ],
)
def test_unit_from_dat(test_workspace, dat_name, group, label, expected_outcome):
    dat_path = Path(test_workspace, dat_name)
    dat = DAT(dat_path)
    unit = getattr(dat, group)[label]
    assert unit.location == expected_outcome
