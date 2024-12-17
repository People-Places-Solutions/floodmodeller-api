from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd
import pytest

from floodmodeller_api.units.superbridge import SUPERBRIDGE

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture()
def lines(test_workspace: Path) -> list[str]:
    path = test_workspace / "superbridge/US_vSP_NoBl_2O_Para.ied"
    with open(path) as file:
        return [line.rstrip("\n") for line in file]


@pytest.fixture()
def unit(lines: list[str]) -> SUPERBRIDGE:
    return SUPERBRIDGE(lines)


def test_read_superbridge(unit: SUPERBRIDGE):
    assert unit.comment == "prototype for rev 3 / No Spill data, no blockage"

    assert unit.name == "Label11"
    assert unit.ds_label == "Label12"
    assert unit.us_remote_label == "CH0001"
    assert unit.ds_remote_label == "CH0002"

    assert unit.revision == 3
    assert unit.bridge_name == "Clifton Suspension Bridge"
    assert unit.subtype == "USBPR"

    assert unit.calibration_coefficient == 1
    assert unit.skew == 0
    assert unit.bridge_width_dual == 0
    assert unit.bridge_dist_dual == 0
    assert unit.total_pier_width == 0
    assert unit.orifice_flow is True
    assert unit.orifice_lower_transition_dist == 0.3
    assert unit.orifice_upper_transition_dist == 0.1
    assert unit.orifice_discharge_coefficient == 1
    assert unit.aligned is True

    assert unit.section_nrows == [4, 0, 0, 0]

    assert unit.opening_type == "PARABOLA1"
    assert unit.opening_nrows == 2
    assert unit.opening_nsubrows == [3, 3]

    assert unit.culvert_nrows == 0

    assert unit.spill_nrows == 3
    assert unit.weir_coefficient == 1.7
    assert unit.modular_limit == 0.9

    assert unit.block_nrows == 0
    assert unit.inlet_loss == 0.5
    assert unit.outlet_loss == 1
    assert unit.block_method == "USDEPTH"
    assert unit.override is False

    expected = {
        "X": [-10.0, -10.0, 10.0, 10.0],
        "Y": [5.0, 0.0, 0.0, 5.0],
        "Mannings n": [0.035, 0.035, 0.035, 0.035],
        "Embankments": ["LEFT", "", "", "RIGHT"],
    }
    pd.testing.assert_frame_equal(unit.section_data[0], pd.DataFrame(expected))

    expected = {"X": [], "Y": [], "Mannings n": [], "Embankments": []}
    pd.testing.assert_frame_equal(unit.section_data[1], pd.DataFrame(expected), check_dtype=False)
    pd.testing.assert_frame_equal(unit.section_data[2], pd.DataFrame(expected), check_dtype=False)
    pd.testing.assert_frame_equal(unit.section_data[3], pd.DataFrame(expected), check_dtype=False)

    expected = {"X": [-7.5, -5.0, -2.5], "Z": [0.0, 5.0, 0.0]}
    pd.testing.assert_frame_equal(unit.opening_data[0], pd.DataFrame(expected))

    expected = {"X": [2.5, 5.0, 7.5], "Z": [0.0, 5.0, 0.0]}
    pd.testing.assert_frame_equal(unit.opening_data[1], pd.DataFrame(expected))

    expected = {
        "Invert": [],
        "Soffit": [],
        "Section Area": [],
        "Cd Part Full": [],
        "Cd Full": [],
        "Drowning Coefficient": [],
    }
    pd.testing.assert_frame_equal(unit.culvert_data, pd.DataFrame(expected), check_dtype=False)

    expected = {
        "X": [-10.0, 0.0, 10.0],
        "Y": [7.0, 9.0, 7.0],
        "Easting": [0.0, 0.0, 0.0],
        "Northing": [0.0, 0.0, 0.0],
    }
    pd.testing.assert_frame_equal(unit.spill_data, pd.DataFrame(expected))

    expected = {"percentage": [], "time": [], "datetime": []}
    pd.testing.assert_frame_equal(unit.block_data, pd.DataFrame(expected), check_dtype=False)


def test_write_superbridge(lines: list[str], unit: SUPERBRIDGE):
    raw_block = unit._write()
    print("\n", "\n".join(raw_block), "\n")
    # assert raw_block == lines
