from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd
import pytest

from floodmodeller_api.units import BRIDGE

if TYPE_CHECKING:
    from pathlib import Path


def create_bridge(path: Path) -> BRIDGE:
    with open(path) as file:
        lines = [line.rstrip("\n") for line in file]
    return BRIDGE(lines)


@pytest.fixture()
def folder(test_workspace: Path) -> Path:
    return test_workspace / "integrated_bridge"


def test_read_bridge(folder: Path):  # noqa: PLR0915 (all needed)
    unit = create_bridge(folder / "US_vSP_NoBl_2O_Para.ied")

    assert unit.comment == "prototype for rev 3 / No Spill data, no blockage"

    assert unit.name == "Label11"
    assert unit.ds_label == "Label12"
    assert unit.us_remote_label == "CH0001"
    assert unit.ds_remote_label == "CH0002"

    assert unit.revision == 3
    assert unit.bridge_name == "Clifton Suspension Bridge"
    assert unit.integrated_subtype == "USBPR"

    assert unit.calibration_coefficient == 1
    assert unit.skew == 0
    assert unit.bridge_width_dual == 0
    assert unit.bridge_dist_dual == 0
    assert unit.total_pier_width == 0
    assert unit.orifice_flow is True
    assert unit.orifice_lower_transition_dist == 0.3
    assert unit.orifice_upper_transition_dist == 0.1
    assert unit.orifice_discharge_coefficient == 1

    assert unit.abutment_type == 3
    assert unit.specify_piers is False
    assert unit.soffit_shape == "FLAT"

    assert unit.aligned is True

    assert unit.section_nrows_list == [4, 0, 0, 0]

    assert unit.opening_type == "PARABOLA1"
    assert unit.opening_nrows == 2
    assert unit.opening_nsubrows_list == [3, 3]

    assert unit.culvert_nrows == 0

    assert unit.spill_nrows == 3
    assert unit.weir_coefficient == 1.7
    assert unit.modular_limit == 0.9

    assert unit.block_nrows == 0
    assert unit.inlet_loss == 0.5
    assert unit.outlet_loss == 1
    assert unit.block_method == "USDEPTH"
    assert unit.override is False

    expected = pd.DataFrame(
        {
            "X": [-10.0, -10.0, 10.0, 10.0],
            "Y": [5.0, 0.0, 0.0, 5.0],
            "Mannings n": [0.035, 0.035, 0.035, 0.035],
            "Panel": ["*", "", "", "*"],
            "Embankments": ["LEFT", "", "", "RIGHT"],
        },
    )
    pd.testing.assert_frame_equal(unit.section_data_list[0], expected)

    expected = pd.DataFrame({"X": [], "Y": [], "Mannings n": [], "Panel": [], "Embankments": []})
    pd.testing.assert_frame_equal(unit.section_data_list[1], expected, check_dtype=False)
    pd.testing.assert_frame_equal(unit.section_data_list[2], expected, check_dtype=False)
    pd.testing.assert_frame_equal(unit.section_data_list[3], expected, check_dtype=False)

    expected = pd.DataFrame({"X": [-7.5, -5.0, -2.5], "Z": [0.0, 5.0, 0.0]})
    pd.testing.assert_frame_equal(unit.opening_data_list[0], expected)

    expected = pd.DataFrame({"X": [2.5, 5.0, 7.5], "Z": [0.0, 5.0, 0.0]})
    pd.testing.assert_frame_equal(unit.opening_data_list[1], expected)

    expected = pd.DataFrame(
        {
            "Invert": [],
            "Soffit": [],
            "Section Area": [],
            "Cd Part Full": [],
            "Cd Full": [],
            "Drowning Coefficient": [],
            "X": [],
        },
    )
    pd.testing.assert_frame_equal(unit.culvert_data, expected, check_dtype=False)

    expected = pd.DataFrame(
        {
            "X": [-10.0, 0.0, 10.0],
            "Y": [7.0, 9.0, 7.0],
            "Easting": [0.0, 0.0, 0.0],
            "Northing": [0.0, 0.0, 0.0],
        },
    )
    pd.testing.assert_frame_equal(unit.spill_data, expected)

    expected = pd.DataFrame({"percentage": [], "time": [], "datetime": []})
    pd.testing.assert_frame_equal(unit.block_data, expected, check_dtype=False)


def test_write_bridge(folder: Path):
    for file in folder.glob("*.ied"):
        unit = create_bridge(folder / file)
        output = unit._write()

        new_unit = BRIDGE(output)
        new_output = new_unit._write()
        assert unit == new_unit, f"unit objects not equal for {file=}"
        assert output == new_output, f"unit outputs not equal for {file=}"
        for line in output:
            assert isinstance(line, str), f"{line=} is not a string"


def test_valid_change(folder: Path):
    unit = create_bridge(folder / "US_vSP_NoBl_2O_Para.ied")

    assert unit.calibration_coefficient == 1
    unit.calibration_coefficient = 10
    assert unit.calibration_coefficient == 10

    output = unit._write()
    new_unit = BRIDGE(output)
    assert new_unit.calibration_coefficient == 10


def test_invalid_change(folder: Path):
    unit = create_bridge(folder / "US_vSP_NoBl_2O_Para.ied")
    unit.calibration_coefficient = "hi"  # type: ignore
    # ignoring typing as this mistake is on purpose
    msg = (
        "One or more parameters in <floodmodeller_api Unit Class:"
        " BRIDGE(name=Label11, type=INTEGRATED)> are invalid:"
        "\n     calibration_coefficient -> Expected: (<class 'float'>, <class 'int'>)"
    )
    with pytest.raises(ValueError, match=re.escape(msg)):
        unit._write()
