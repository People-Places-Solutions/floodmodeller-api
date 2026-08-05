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

import pandas as pd
import pytest

from floodmodeller_api import DAT
from floodmodeller_api.units import CONDUIT


def test_create_from_blank_with_params_conduit_section():
    "Test to create a SECTION CONDUIT from blank, with parameters specified."

    coords = pd.DataFrame(
        {
            "x": [0, 1, 2],
            "y": [0, 0.5, 2],
            "cw_friction": [1.5, 1.5, 1.5],
        },
    )

    unit = CONDUIT(
        name="testing",
        spill="spill1",
        comment="Testing that the unit can be created with parameters.",
        subtype="SECTION",
        dist_to_next=5,
        coords=coords,
    )

    assert unit._write() == [
        "CONDUIT Testing that the unit can be created with parameters.",
        "SECTION",
        "testing     spill1      ",
        "         5",
        "         3",  # Number of coordinate points below
        "     0.000     0.000  1.500000",
        "     1.000     0.500  1.500000",
        "     2.000     2.000  1.500000",
    ]


FULLARCH_DAT_FILE = "repeated_FULLARCH.DAT"

FULLARCH_EXPECTED_CASES = [
    (
        "FULLARCH_01",
        {
            "name": "FULLARCH_01",
            "comment": "Comment with text!",
            "subtype": "FULLARCH",
            "dist_to_next": 20.0,
            "friction_eq": "MANNING",
            "invert": 50.0,
            "width": 6.0,
            "height": 3.0,
            "use_bottom_slot": "ON",
            "top_slot_dist": 0.001,
            "bottom_slot_depth": 1.0,
            "use_top_slot": "ON",
            "bottom_slot_dist": 0.002,
            "top_slot_depth": 0.75,
            "friction_on_invert": 0.035,
            "friction_on_arch": 0.04,
        },
    ),
    (
        "FULLARCH_02",
        {
            "name": "FULLARCH_02",
            "comment": "Comment with text! Note CW friction on this one",
            "subtype": "FULLARCH",
            "dist_to_next": 0.0,
            "friction_eq": "COLEBROOK-WHITE",
            "invert": 50.0,
            "width": 6.0,
            "height": 3.0,
            "use_bottom_slot": "OFF",
            "top_slot_dist": 0.0,
            "bottom_slot_depth": 0.0,
            "use_top_slot": "GLOBAL",
            "bottom_slot_dist": 0.0,
            "top_slot_depth": 0.0,
            "friction_on_invert": 0.02,
            "friction_on_arch": 0.2,
        },
    ),
]

FULLARCH_UNIT_NAMES = [unit_name for unit_name, _ in FULLARCH_EXPECTED_CASES]


@pytest.fixture()
def fullarch_dat(test_workspace):
    """Load the DAT file containing the FULLARCH conduits."""

    return DAT(test_workspace / FULLARCH_DAT_FILE)


@pytest.fixture()
def fullarch_conduits(fullarch_dat):
    """Return the conduit units from the FULLARCH test file."""

    return fullarch_dat.conduits


@pytest.mark.parametrize(
    ("unit_name", "expected"),
    FULLARCH_EXPECTED_CASES,
)
def test_read_fullarch_units(
    fullarch_conduits,
    unit_name,
    expected,
):
    """Test that both FULLARCH conduits are parsed correctly."""

    unit = fullarch_conduits[unit_name]

    assert isinstance(unit, CONDUIT)

    for attribute, expected_value in expected.items():
        actual_value = getattr(unit, attribute)

        if isinstance(expected_value, float):
            assert actual_value == pytest.approx(expected_value)
        else:
            assert actual_value == expected_value


def test_both_fullarch_units_are_loaded(fullarch_conduits):
    """Test that neither FULLARCH conduit overwrites the other."""

    assert set(FULLARCH_UNIT_NAMES).issubset(fullarch_conduits)


def test_fullarch_unit_count(fullarch_conduits):
    """Test that the DAT file contains exactly two FULLARCH conduits."""

    fullarch_units = [
        unit
        for unit in fullarch_conduits.values()
        if isinstance(unit, CONDUIT) and unit.subtype == "FULLARCH"
    ]

    assert len(fullarch_units) == 2


def test_fullarch_units_retain_distinct_values(fullarch_conduits):
    """Test that values from the two FULLARCH blocks remain distinct."""

    manning = fullarch_conduits["FULLARCH_01"]
    colebrook_white = fullarch_conduits["FULLARCH_02"]

    assert manning.dist_to_next == pytest.approx(20.0)
    assert colebrook_white.dist_to_next == pytest.approx(0.0)

    assert manning.friction_eq == "MANNING"
    assert colebrook_white.friction_eq == "COLEBROOK-WHITE"

    assert manning.use_bottom_slot == "ON"
    assert colebrook_white.use_bottom_slot == "OFF"

    assert manning.use_top_slot == "ON"
    assert colebrook_white.use_top_slot == "GLOBAL"

    assert manning.friction_on_invert == pytest.approx(0.035)
    assert colebrook_white.friction_on_invert == pytest.approx(0.02)

    assert manning.friction_on_arch == pytest.approx(0.04)
    assert colebrook_white.friction_on_arch == pytest.approx(0.2)


@pytest.mark.parametrize(
    "unit_name",
    FULLARCH_UNIT_NAMES,
)
def test_fullarch_read_write_round_trip(
    fullarch_conduits,
    unit_name,
):
    """Test that each FULLARCH conduit survives writing and rereading."""

    original = fullarch_conduits[unit_name]

    reread = CONDUIT(original._write())

    assert reread == original


@pytest.mark.parametrize(
    "unit_name",
    FULLARCH_UNIT_NAMES,
)
def test_fullarch_written_output_contains_unit_type(
    fullarch_conduits,
    unit_name,
):
    """Test that written output retains the conduit type and unit name."""

    written = fullarch_conduits[unit_name]._write()

    assert written[0].startswith("CONDUIT")
    assert written[1] == "FULLARCH"
    assert unit_name in written[2]
