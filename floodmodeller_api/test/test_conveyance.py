from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy.spatial.distance import directed_hausdorff
from shapely.geometry import LineString, Polygon

from floodmodeller_api import DAT
from floodmodeller_api.units.conveyance import (
    calculate_conveyance_by_panel,
    calculate_conveyance_part,
    calculate_cross_section_conveyance,
    insert_intermediate_wls,
)


def test_calculate_cross_section_conveyance():
    x = np.array([0, 1, 2, 3, 4])
    y = np.array([5, 3, 1, 2, 6])
    n = np.array([0.03, 0.03, 0.03, 0.03, 0.03])
    panel_markers = np.array([False, False, False, False, False])
    rpl = np.array([1.0, 1.0, 1.0, 1.0, 1.0])
    result = calculate_cross_section_conveyance(x, y, n, rpl, panel_markers)

    assert isinstance(result, pd.Series), "Result should be a pandas Series"
    assert not result.empty, "Result should not be empty"


def test_calculate_conveyance_by_panel():
    x = np.array([0, 1, 2])
    y = np.array([5, 3, 1])
    n = np.array([0.03, 0.03])
    rpl = 1.0
    wls = np.array([1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0])

    result = calculate_conveyance_by_panel(x, y, n, rpl, wls)

    assert isinstance(result, list), "Result should be a list"
    assert len(result) == len(wls), "Result length should match the length of water levels"
    assert all(isinstance(val, float) for val in result), "All conveyance values should be floats"


def test_calculate_conveyance_part():
    wetted_polygon = Polygon([(1, 3), (2, 1), (3, 2), (4, 6), (1, 3)])
    water_plane = LineString([(0, 3), (5, 3)])
    glass_walls = LineString([(1, 3), (1, 7)]), LineString([(4, 6), (4, 7)])
    x = np.array([1, 2, 3, 4])
    n = np.array([0.03, 0.03, 0.03, 0.03])
    rpl = 1.0

    result = calculate_conveyance_part(wetted_polygon, water_plane, glass_walls, x, n, rpl)

    assert isinstance(result, float), "Result should be a float"
    assert result >= 0, "Conveyance should be non-negative"


def test_insert_intermediate_wls():
    arr = np.array([1.0, 2.0, 3.0])
    threshold = 0.5

    result = insert_intermediate_wls(arr, threshold)

    assert isinstance(result, np.ndarray), "Result should be a numpy array"
    assert result[0] == 1.0 and result[-1] == 3.0, "First and last elements should match the input"
    assert all(np.diff(result) <= threshold), "All gaps should be <= to the threshold"


@pytest.fixture(scope="module")
def dat(test_workspace: Path):
    return DAT(test_workspace / "conveyance_test.dat")


@pytest.fixture(scope="module")
def from_gui(test_workspace: Path):
    return pd.read_csv(test_workspace / "expected_conveyance.csv")


@pytest.mark.parametrize("section", ("a", "a2", "b", "b2", "c", "d", "d2", "e", "e2", "e3"))
def test_results_close_to_gui(section: str, dat: DAT, from_gui: pd.DataFrame):
    threshold = 6

    actual = dat.sections[section].conveyance
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


@pytest.mark.parametrize("section", ("a", "a2", "b", "b2", "c", "d", "d2", "e", "e2", "e3"))
def test_results_match_gui_at_shared_points(section: str, dat: DAT, from_gui: pd.DataFrame):
    tolerance = 1e-2  # 0.001
    actual = dat.sections[section].conveyance
    expected = (
        from_gui.set_index(f"{section}_stage")[f"{section}_conveyance"].dropna().drop_duplicates()
    )
    shared_index = sorted(set(actual.index).intersection(expected.index))
    diff = expected[shared_index] - actual[shared_index]
    assert (abs(diff) < tolerance).all()  # asserts all conveyance values within 0.001 difference
