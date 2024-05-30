import pytest
import numpy as np
import pandas as pd
from shapely.geometry import LineString, Polygon

from floodmodeller_api.units.conveyance import (
    calculate_cross_section_conveyance,
    calculate_conveyance_by_panel,
    calculate_conveyance_part,
    insert_intermediate_wls
)

# Helper function to create simple cross-section data
def create_simple_cross_section():
    x = np.array([0, 1, 2, 3, 4])
    y = np.array([1, 2, 1, 2, 1])
    n = np.array([0.03, 0.03, 0.03, 0.03, 0.03])
    panel_markers = np.array([True, False, True, False, True])
    return x, y, n, panel_markers

def test_calculate_cross_section_conveyance():
    x, y, n, panel_markers = create_simple_cross_section()
    result = calculate_cross_section_conveyance(x, y, n, panel_markers)
    
    assert isinstance(result, pd.Series), "Result should be a pandas Series"
    assert not result.empty, "Result should not be empty"
    
def test_calculate_conveyance_by_panel():
    x = np.array([0, 1, 2])
    y = np.array([1, 2, 1])
    n = np.array([0.03, 0.03])
    wls = np.array([1.0, 1.5, 2.0])
    
    result = calculate_conveyance_by_panel(x, y, n, wls)
    
    assert isinstance(result, list), "Result should be a list"
    assert len(result) == len(wls), "Result length should match the length of water levels"
    assert all(isinstance(val, float) for val in result), "All conveyance values should be floats"
    
def test_calculate_conveyance_part():
    wetted_polygon = Polygon([(0, 1), (1, 2), (2, 1), (0, 1)])
    water_plane = LineString([(0, 1.5), (2, 1.5)])
    glass_wall_left = LineString([(0, 1), (0, 2)])
    glass_wall_right = LineString([(2, 1), (2, 2)])
    average_mannings = 0.03
    
    result = calculate_conveyance_part(
        wetted_polygon, water_plane, glass_wall_left, glass_wall_right, average_mannings
    )
    
    assert isinstance(result, float), "Result should be a float"
    assert result >= 0, "Conveyance should be non-negative"
    
def test_insert_intermediate_wls():
    arr = np.array([1.0, 2.0, 3.0])
    threshold = 0.5
    result = insert_intermediate_wls(arr, threshold)
    
    assert isinstance(result, np.ndarray), "Result should be a numpy array"
    assert result[0] == 1.0 and result[-1] == 3.0, "First and last elements should match the input"
    assert all(np.diff(result) <= threshold), "All gaps should be <= to the threshold"
    
# Run the tests
if __name__ == "__main__":
    pytest.main()
