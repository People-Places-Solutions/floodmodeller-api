from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd
from shapely import LineString, MultiLineString, Polygon, intersection

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
    # Create a set of water levels to calculate conveyance at,
    # currently using 50mm minimum increments plus WLs at every data point
    wls = insert_intermediate_wls(np.unique(y), threshold=0.05)

    # Panel markers are forced true to the bounds to make the process work
    panel_markers = np.array([True, *panel_markers[1:-1], True])
    panel_indices = np.where(panel_markers)[0]
    panel_start_indices = panel_indices[:-1]
    panel_end_indices = panel_indices[1:] + 1
    conveyance_by_panel = [
        calculate_conveyance_by_panel(
            x[panel_start:panel_end],
            y[panel_start:panel_end],
            n[panel_start:panel_end],
            (
                1.0
                if (panel_start == 0 and not panel_markers[0]) or rpl[panel_start] == 0
                else float(rpl[panel_start])
            ),
            wls,
        )
        for panel_start, panel_end in zip(panel_start_indices, panel_end_indices)
    ]

    # Sum conveyance across panels
    conveyance_values = [sum(values) for values in zip(*conveyance_by_panel)]

    return pd.Series(data=conveyance_values, index=wls)


def calculate_geometry(
    x: np.ndarray,
    y: np.ndarray,
    n: np.ndarray,
    water_level: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Calculate area, length, weighted mannings for piecewise linear curve (x, y) below water_level.

    Args:
        x (np.ndarray): 1D array of x-coordinates.
        y (np.ndarray): 1D array of y-coordinates.
        n (np.ndarray): 1D array to integrate over the length.
        water_level (np.ndarray): The horizontal reference line.

    Returns:
        np.ndarray: The area above the curve and under the reference line.
        np.ndarray: The length of the curve under the reference line.
        np.ndarray: Manning's n integrated along the curve under the reference line.
    """
    h = water_level[:, np.newaxis] - y

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

    total_area = np.sum(area, axis=1)
    total_length = np.sum(length, axis=1)
    total_wetted_mannings = np.sum(weighted_mannings, axis=1)

    return total_area, total_length, total_wetted_mannings


def calculate_conveyance_by_panel(
    x: np.ndarray,
    y: np.ndarray,
    n: np.ndarray,
    rpl: float,
    wls: np.ndarray,
) -> list[float]:
    """
    Calculate the conveyance for a single panel of a cross-section at specified water levels.

    Args:
        x (np.ndarray): The x-coordinates of the panel.
        y (np.ndarray): The y-coordinates of the panel.
        n (np.ndarray): Manning's n values for each segment in the panel.
        rpl (float): Relative Path Length for each segment in the panel.
        wls (np.ndarray): The water levels at which to calculate conveyance.

    Returns:
        list[float]: A list of conveyance values for each water level.
    """

    max_y = np.max(wls) + 1
    min_y = np.min(wls) - 1

    # insert additional start/end points to represent the glass wall sides
    x = np.array([x[0], *x, x[-1]])
    y = np.array([max_y, *y, max_y])
    n = np.array([0, *n, 0])

    # Define a polygon for the channel including artificial sides and top
    channel_polygon = Polygon(zip(x, y))
    start, end = x[0] - 0.1, x[-1] + 0.1  # Useful points enclosing the x bounds with small buffer

    # Define linestring geometries representing glass walls, so they can be subtracted later
    glass_walls = (
        LineString(zip([x[0], x[1]], [y[0], y[1]])),  # left
        LineString(zip([x[-2], x[-1]], [y[-2], y[-1]])),  # right
    )

    # Remove glass wall sections from coords
    x, y, n = x[1:-1], y[1:-1], n[1:-1]

    conveyance_values = []
    for wl in wls:
        if wl <= np.min(y):
            # no channel capacity (essentially zero depth) so no need to calculate
            conveyance_values.append(0.0)
            continue

        # Some geometries to represent the channel at a given water level
        water_surface = Polygon(zip([start, start, end, end], [wl, min_y, min_y, wl]))
        water_plane = intersection(channel_polygon, LineString(zip([start, end], [wl, wl])))
        wetted_polygon = intersection(channel_polygon, water_surface)

        multiple_parts = wetted_polygon.geom_type in ["GeometryCollection", "MultiPolygon"]
        parts = wetted_polygon.geoms if multiple_parts else [wetted_polygon]

        # 'parts' here refers to when a water level results in 2 separate channel sections,
        # e.g. where the cross section has a 'peak' part way through
        conveyance = sum(
            calculate_conveyance_part(part, water_plane, glass_walls, x, n, rpl) for part in parts
        )
        conveyance_values.append(conveyance)

    return conveyance_values


def calculate_conveyance_part(  # noqa: PLR0913
    wetted_polygon: Polygon,
    water_plane: LineString,
    glass_walls: tuple[LineString, LineString],
    x: np.ndarray,
    n: np.ndarray,
    rpl: float,
) -> float:
    """
    Calculate the conveyance for a part of the wetted area.

    Args:
        wetted_polygon (Polygon): The polygon representing the wetted area.
        water_plane (LineString): The line representing the water plane.
        glass_wall_left (LineString): The left boundary of the channel.
        glass_wall_right (LineString): The right boundary of the channel.
        x (np.ndarray): 1D array of channel chainage
        n (np.ndarray): 1D array of channel mannings
        rpl (float): Relative path length of panel

    Returns:
        float: The conveyance value for the wetted part.
    """
    water_plane_clip: LineString = intersection(water_plane, wetted_polygon)
    glass_wall_left_clip: LineString = intersection(glass_walls[0], wetted_polygon)
    glass_wall_right_clip: LineString = intersection(glass_walls[1], wetted_polygon)

    # wetted perimeter should only account for actual section of channel, so we need to remove any
    # length related to the water surface and any glass walls due to panel
    perimeter_loss = (
        water_plane_clip.length + glass_wall_left_clip.length + glass_wall_right_clip.length
    )

    wetted_perimeter = wetted_polygon.boundary.length - perimeter_loss
    if wetted_perimeter < MINIMUM_PERIMETER_THRESHOLD:
        # Would occur if water level is above lowest point on section, but intersects a near-zero
        # perimeter, e.g. touching the bottom of an elevated side channel
        return 0.0

    area = wetted_polygon.area

    wetted_polyline: LineString = (
        wetted_polygon.exterior.difference(water_plane_clip)
        .difference(glass_wall_left_clip)
        .difference(glass_wall_right_clip)
    )
    weighted_mannings = calculate_weighted_mannings(x, n, rpl, wetted_polyline)

    # apply conveyance equation
    return (area ** (5 / 3) / wetted_perimeter ** (2 / 3)) * (wetted_perimeter / weighted_mannings)


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


def calculate_weighted_mannings(
    x: np.ndarray,
    n: np.ndarray,
    rpl: float,
    wetted_polyline: LineString,
) -> float:
    """Calculate the weighted Manning's n value for a wetted polyline."""

    segments = line_to_segments(wetted_polyline)
    segment_starts = segments[:, 0, 0]
    segment_ends = segments[:, 1, 0]

    mannings_values = get_mannings_by_segment_x_coords(x, n, segment_starts, segment_ends)
    segment_lengths = np.linalg.norm(segments[:, 1] - segments[:, 0], axis=1)

    return np.sum(mannings_values * segment_lengths * np.sqrt(rpl))


def line_to_segments(line: LineString | MultiLineString) -> np.ndarray:
    """Convert a LineString or MultiLineString into an array of segment coordinates."""
    if isinstance(line, LineString):
        coords = np.array(line.coords)
        segments = np.stack((coords[:-1], coords[1:]), axis=1)
        indices = np.argsort(segments[:, :, 0], axis=1)
        return np.take_along_axis(segments, indices[:, :, np.newaxis], axis=1)
    if isinstance(line, MultiLineString):
        return np.concatenate([line_to_segments(geom) for geom in line.geoms])
    raise TypeError("Input must be a LineString or MultiLineString")


def get_mannings_by_segment_x_coords(
    x: np.ndarray,
    n: np.ndarray,
    start_x: np.ndarray,
    end_x: np.ndarray,
) -> np.ndarray:
    """Get the Manning's n or RPL value for segments based on their start x-coordinates."""

    mannings_values = np.zeros_like(start_x)

    # Handle vertical segments by taking the first x match
    vertical_segments = start_x == end_x
    vertical_indices = np.searchsorted(x, start_x[vertical_segments])
    mannings_values[vertical_segments] = n[vertical_indices]

    # Handle non-vertical segments by taking the last match
    non_vertical_segments = start_x != end_x
    non_vertical_indices = np.searchsorted(x, start_x[non_vertical_segments], side="right") - 1
    mannings_values[non_vertical_segments] = n[non_vertical_indices]

    return mannings_values


@lru_cache
def calculate_cross_section_conveyance_chached(
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
