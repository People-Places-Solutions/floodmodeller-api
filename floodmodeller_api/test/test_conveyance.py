from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_array_almost_equal
from scipy.spatial.distance import directed_hausdorff

from floodmodeller_api import DAT
from floodmodeller_api.units.conveyance import (
    calculate_cross_section_conveyance,
    calculate_geometry,
    insert_intermediate_wls,
)

if TYPE_CHECKING:
    from pathlib import Path


def test_calculate_cross_section_conveyance():
    x = np.array([0, 1, 2, 3, 4])
    y = np.array([5, 3, 1, 2, 6])
    n = np.array([0.03, 0.03, 0.03, 0.03, 0.03])
    panel_markers = np.array([False, False, False, False, False])
    rpl = np.array([1.0, 1.0, 1.0, 1.0, 1.0])
    result = calculate_cross_section_conveyance(x, y, n, rpl, panel_markers)

    assert isinstance(result, pd.Series), "Result should be a pandas Series"
    assert not result.empty, "Result should not be empty"


def test_insert_intermediate_wls():
    arr = np.array([1.0, 2.0, 3.0])
    threshold = 0.5

    result = insert_intermediate_wls(arr, threshold)

    assert isinstance(result, np.ndarray), "Result should be a numpy array"
    assert result[0] == 1.0, "First element should match the input"
    assert result[-1] == 3.0, "Last element should match the input"
    assert all(np.diff(result) <= threshold), "All gaps should be <= to the threshold"


@pytest.fixture(scope="module")
def dat(test_workspace: Path):
    return DAT(test_workspace / "conveyance_test.dat")


@pytest.fixture(scope="module")
def from_gui(test_workspace: Path):
    return pd.read_csv(test_workspace / "expected_conveyance.csv")


@pytest.mark.parametrize("section", ["a", "a2", "b", "b2", "c", "d", "d2", "e", "e2", "e3"])
def test_results_close_to_gui(section: str, dat: DAT, from_gui: pd.DataFrame):
    threshold = 6

    actual = dat.sections[section].conveyance  # type: ignore
    # ignored because we know that these all have type RIVER

    expected = (
        from_gui.set_index(f"{section}_stage")[f"{section}_conveyance"].dropna().drop_duplicates()
    )
    common_index = sorted(set(actual.index).union(expected.index))
    actual_interpolated = actual.reindex(common_index).interpolate(method="slinear")
    expected_interpolated = expected.reindex(common_index).interpolate(method="slinear")

    u = np.array(list(zip(actual_interpolated.index, actual_interpolated)))
    v = np.array(list(zip(expected_interpolated.index, expected_interpolated)))
    hausdorff_distance = directed_hausdorff(u, v)[0]

    assert hausdorff_distance < threshold


@pytest.mark.parametrize("section", ["a", "a2", "b", "b2", "c", "d", "d2", "e", "e2", "e3"])
def test_results_match_gui_at_shared_points(section: str, dat: DAT, from_gui: pd.DataFrame):
    tolerance = 1e-2  # 0.01

    actual = dat.sections[section].conveyance  # type: ignore
    # ignored because we know that these all have type RIVER

    expected = (
        from_gui.set_index(f"{section}_stage")[f"{section}_conveyance"].dropna().drop_duplicates()
    )
    shared_index = sorted(set(actual.index).intersection(expected.index))
    diff = expected[shared_index] - actual[shared_index]
    assert (abs(diff) < tolerance).all()  # asserts all conveyance values within 0.01 difference


def test_calculate_geometry():
    # area example from https://blogs.sas.com/content/iml/2022/11/21/area-under-curve.html
    x = np.array([1, 2, 3.5, 4, 5, 6, 6.5, 7, 8, 10, 12, 15])
    y = np.array([-0.5, -0.1, 0.2, 0.7, 0.8, -0.2, 0.3, 0.6, 0.3, 0.1, -0.4, -0.6])
    n = np.array([1, 2, 3.5, 0, 0, 0, 0, 0, 0, 5, 6, 7])
    water_levels = np.array([-1, 0, 1])
    area, length, mannings = calculate_geometry(x, y, n, water_levels)
    total_area = np.sum(area, axis=1)
    total_length = np.sum(length, axis=1)
    total_mannings = np.sum(mannings, axis=1)
    assert_array_almost_equal(total_area, np.array([0, 2.185, 13.65]))
    assert_array_almost_equal(total_length, np.array([0, 6.808522, 15.145467]))
    assert_array_almost_equal(total_mannings, np.array([0, 28.383004, 34.959038]))
