from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd

MINIMUM_PERIMETER_THRESHOLD = 1e-8


def calculate_cross_section_conveyance(
    x: np.ndarray,
    y: np.ndarray,
    n: np.ndarray,
    rpl: np.ndarray,
    panel_markers: np.ndarray,
) -> pd.Series:
    """
    Calculate the conveyance of a cross-section by summing the conveyance
    across all panels defined by panel markers.

    Args:
        x (np.ndarray): The x-coordinates of the cross-section.
        y (np.ndarray): The y-coordinates of the cross-section.
        n (np.ndarray): Manning's n values for each segment.
        rpl (np.ndarray): Relative Path Length values for each segment.
        panel_markers (np.ndarray): Boolean array indicating the start of each panel.

    Returns:
        pd.Series: A pandas Series containing the conveyance values indexed by water levels.

    Example:
        .. code-block:: python

            x = np.array([0, 1, 2, 3, 4])
            y = np.array([1, 2, 1, 2, 1])
            n = np.array([0.03, 0.03, 0.03, 0.03, 0.03])
            rpl = np.array([1., 1., 1., 1., 1.])
            panel_markers = np.array([True, False, True, False, True])
            result = calculate_cross_section_conveyance(x, y, n, rpl, panel_markers)
            print(result)
    """
    water_levels = insert_intermediate_wls(np.unique(y), threshold=0.05)
    area, length, mannings = calculate_geometry(x, y, n, water_levels)
    panel = panel_markers.cumsum()[:-1]

    intersection = (y[:-2] < water_levels[:, np.newaxis]) & (y[1:-1] > water_levels[:, np.newaxis])
    false_column = np.full((intersection.shape[0], 1), False)
    section_markers = np.hstack([false_column, intersection])
    section = section_markers.cumsum(axis=1)

    conveyance = np.zeros_like(water_levels)
    for i in range(panel.max() + 1):
        in_panel = panel == i
        if not in_panel.any():
            continue
        rpl_panel = np.sqrt(rpl[:-1][in_panel][0])
        rpl_panel = 1 if rpl_panel == 0 else rpl_panel
        for j in range(section.max() + 1):
            in_panel_and_section = in_panel & (section == j)
            if not in_panel_and_section.any():
                continue
            total_area = np.where(in_panel_and_section, area, 0).sum(axis=1)
            total_length = np.where(in_panel_and_section, length, 0).sum(axis=1)
            total_mannings = np.where(in_panel_and_section, mannings, 0).sum(axis=1)
            conveyance_section = (
                total_area ** (5 / 3) * total_length ** (1 / 3) / (total_mannings * rpl_panel)
            )

            is_valid = total_length >= MINIMUM_PERIMETER_THRESHOLD
            conveyance += np.where(is_valid, conveyance_section, 0)

    return pd.Series(conveyance, index=water_levels)


def calculate_geometry(
    x: np.ndarray,
    y: np.ndarray,
    n: np.ndarray,
    water_levels: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Calculate area, length, weighted mannings for piecewise linear curve (x, y) below water_level.

    Args:
        x (np.ndarray): 1D array of x-coordinates.
        y (np.ndarray): 1D array of y-coordinates.
        n (np.ndarray): 1D array to integrate over the length.
        water_levels (np.ndarray): The horizontal reference line.

    Returns:
        np.ndarray: The area above the curve and under the reference line.
        np.ndarray: The length of the curve under the reference line.
        np.ndarray: Manning's n integrated along the curve under the reference line.
    """
    h = water_levels[:, np.newaxis] - y

    x1 = x[:-1]
    x2 = x[1:]
    h1 = h[:, :-1]
    h2 = h[:, 1:]
    n1 = n[:-1]
    n2 = n[1:]

    dx = x2 - x1

    is_submerged = (h1 > 0) & (h2 > 0)
    is_submerged_on_left = (h1 > 0) & (h2 <= 0)
    is_submerged_on_right = (h1 <= 0) & (h2 > 0)
    conditions = [is_submerged, is_submerged_on_left, is_submerged_on_right]

    # needed for partially submerged sections
    dx_left = dx * h1 / (h1 - h2)
    dx_right = dx * h2 / (h2 - h1)
    n_left = n1 + (n2 - n1) * dx_left / dx
    n_right = n2 + (n1 - n2) * dx_right / dx

    area = np.select(
        conditions,
        [
            0.5 * dx * (h1 + h2),
            0.5 * dx_left * h1,
            0.5 * dx_right * h2,
        ],
        default=0,
    )
    length = np.select(
        conditions,
        [
            np.sqrt((h2 - h1) ** 2 + dx**2),
            np.sqrt(h1**2 + dx_left**2),
            np.sqrt(h2**2 + dx_right**2),
        ],
        default=0,
    )
    weighted_mannings = np.select(
        conditions,
        [
            0.5 * (n1 + n2) * length,
            0.5 * (n1 + n_left) * length,
            0.5 * (n2 + n_right) * length,
        ],
        default=0,
    )

    return area, length, weighted_mannings


def insert_intermediate_wls(arr: np.ndarray, threshold: float) -> np.ndarray:
    """
    Insert intermediate water levels into an array based on a threshold.

    Args:
        arr (np.ndarray): The array of original water levels.
        threshold (float): The maximum allowed gap between water levels.

    Returns:
        np.ndarray: The array with intermediate water levels inserted.
    """
    # Calculate gaps between consecutive elements
    gaps = np.diff(arr)

    # Calculate the number of points needed for each gap
    num_points = (gaps // threshold).astype(int)

    # Prepare lists to hold the new points and results
    new_points = [
        np.linspace(start, end, num + 2, endpoint=False)
        for start, end, num in zip(arr[:-1], arr[1:], num_points)
    ]
    end = np.array([arr[-1]])
    return np.concatenate([*new_points, end])


@lru_cache
def calculate_cross_section_conveyance_cached(
    x: tuple[float],
    y: tuple[float],
    n: tuple[float],
    rpl: tuple[float],
    panel_markers: tuple[float],
) -> pd.Series:
    """Dummy function to allow for caching of the conveyance function as numpy arrays are not
    hashable
    """

    return calculate_cross_section_conveyance(
        np.array(x),
        np.array(y),
        np.array(n),
        np.array(rpl),
        np.array(panel_markers),
    )
