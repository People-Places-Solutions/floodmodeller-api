import numpy as np
import pandas as pd
from shapely import LineString, Polygon, intersection, MultiLineString


def calculate_cross_section_conveyance(
    x: np.ndarray, y: np.ndarray, n: np.ndarray, panel_markers: np.array
) -> pd.Series:
    """
    Calculate the conveyance of a cross-section by summing the conveyance
    across all panels defined by panel markers.

    Args:
        x (np.ndarray): The x-coordinates of the cross-section.
        y (np.ndarray): The y-coordinates of the cross-section.
        n (np.ndarray): Manning's n values for each segment.
        panel_markers (np.ndarray): Boolean array indicating the start of each panel.

    Returns:
        pd.Series: A pandas Series containing the conveyance values indexed by water levels.

    Example:
        .. code-block:: python

            x = np.array([0, 1, 2, 3, 4])
            y = np.array([1, 2, 1, 2, 1])
            n = np.array([0.03, 0.03, 0.03, 0.03, 0.03])
            panel_markers = np.array([True, False, True, False, True])
            result = calculate_cross_section_conveyance(x, y, n, panel_markers)
            print(result)
    """
    wls = insert_intermediate_wls(np.unique(y), threshold=0.05)
    panel_markers = np.array([True, *panel_markers[1:-1], True])
    panel_indices = np.where(panel_markers)[0]
    conveyance_by_panel = []
    for panel_start, panel_end in zip(panel_indices[:-1], panel_indices[1:] + 1):
        panel_x = x[panel_start:panel_end]
        panel_y = y[panel_start:panel_end]
        panel_n = n[panel_start:panel_end]
        conveyance_by_panel.append(calculate_conveyance_by_panel(panel_x, panel_y, panel_n, wls))

    # Sum conveyance across panels
    conveyance_values = [sum(values) for values in zip(*conveyance_by_panel)]

    return pd.Series(data=conveyance_values, index=wls)


def calculate_conveyance_by_panel(
    x: np.ndarray, y: np.ndarray, n: np.ndarray, wls: np.array
) -> list[float]:
    """
    Calculate the conveyance for a single panel of a cross-section at specified water levels.

    Args:
        x (np.ndarray): The x-coordinates of the panel.
        y (np.ndarray): The y-coordinates of the panel.
        n (np.ndarray): Manning's n values for each segment in the panel.
        wls (np.ndarray): The water levels at which to calculate conveyance.

    Returns:
        list[float]: A list of conveyance values for each water level.
    """
    x = np.array([x[0], *x, x[-1]])  # insert additional start/end points
    n = np.array([0, *n, 0])
    max_y = np.max(wls) + 1
    min_y = np.min(wls) - 1
    y = np.array([max_y, *y, max_y])
    channel_polygon = Polygon(zip(x, y))
    start, end = x[0] - 0.1, x[-1] + 0.1
    glass_wall_left = LineString(zip([x[0], x[1]], [y[0], y[1]]))
    glass_wall_right = LineString(zip([x[-2], x[-1]], [y[-2], y[-1]]))

    # Remove glass wall sections from coords
    x, y, n = x[1:-1], y[1:-1], n[1:-1]

    conveyance_values = []
    for wl in wls:
        if wl <= np.min(y):
            conveyance_values.append(0.0)
            continue
        water_surface = Polygon(zip([start, start, end, end], [wl, min_y, min_y, wl]))
        water_plane = intersection(channel_polygon, LineString(zip([start, end], [wl, wl])))
        wetted_polygon = intersection(channel_polygon, water_surface)


        multiple_parts = wetted_polygon.geom_type in ["GeometryCollection", "MultiPolygon"]
        parts = wetted_polygon.geoms if multiple_parts else [wetted_polygon]

        conveyance = 0
        for part in parts:
            conveyance += calculate_conveyance_part(
                part, water_plane, glass_wall_left, glass_wall_right, x, n
            )
        conveyance_values.append(conveyance)

    return conveyance_values


def calculate_conveyance_part(
    wetted_polygon: Polygon,
    water_plane: LineString,
    glass_wall_left: LineString,
    glass_wall_right: LineString,
    x: np.ndarray,
    n: np.ndarray,
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

    Returns:
        float: The conveyance value for the wetted part.
    """
    water_plane_clip = intersection(water_plane, wetted_polygon)
    glass_wall_left_clip = intersection(glass_wall_left, wetted_polygon)
    glass_wall_right_clip = intersection(glass_wall_right, wetted_polygon)
    perimeter_loss = (
        water_plane_clip.length + glass_wall_left_clip.length + glass_wall_right_clip.length
    )

    wetted_perimeter = wetted_polygon.boundary.length - perimeter_loss
    if wetted_perimeter < 1e-8:
        return 0.0

    area = wetted_polygon.area

    wetted_polyline = (
        wetted_polygon.exterior.difference(water_plane_clip)
        .difference(glass_wall_left_clip)
        .difference(glass_wall_right_clip)
    )
    weighted_mannings = calculate_weighted_mannings(x, n, wetted_polyline)

    return (area ** (5 / 3) / wetted_perimeter ** (2 / 3)) * (wetted_perimeter / weighted_mannings)


def insert_intermediate_wls(arr: np.ndarray, threshold: float):
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
    new_points = []

    for i, start in enumerate(arr[:-1]):
        end = arr[i + 1]
        if num_points[i] > 0:
            points = np.linspace(start, end, num_points[i] + 2)[1:-1]
            new_points.extend(points)
        new_points.append(end)

    # Combine the original starting point with the new points
    result = np.array([arr[0]] + new_points)

    return result


def calculate_weighted_mannings(x: np.ndarray, n: np.ndarray, wetted_polyline: LineString) -> float:
    """Calculate the weighted Manning's n value for a wetted polyline."""
    # TODO: handle varying RPL
    rpl = 1  # simple assumption for now...
    segments = line_to_segments(wetted_polyline)
    weighted_mannings = 0
    for segment in segments:
        mannings_value = get_mannings_by_segment_x_coords(
            x, n, segment.coords[0][0], segment.coords[1][0]
        )
        weighted_mannings += mannings_value * segment.length * np.sqrt(rpl)

    return weighted_mannings


def line_to_segments(line: LineString | MultiLineString) -> list[LineString]:
    """Convert a LineString or MultiLineString into a list of LineString segments."""
    if isinstance(line, LineString):
        segments = []
        for start, end in zip(line.coords[:-1], line.coords[1:]):
            points = sorted([start, end], key=lambda x: x[0])
            segments.append(LineString(points))
        return segments
    elif isinstance(line, MultiLineString):
        segments = []
        for linestring in line.geoms:
            segments.extend(line_to_segments(linestring))
        return segments
    else:
        raise TypeError("Input must be a LineString or MultiLineString")


def get_mannings_by_segment_x_coords(
    x: np.ndarray, n: np.ndarray, start_x: float, end_x: float
) -> float:
    """Get the Manning's n value for a segment based on its start x-coordinate."""
    if start_x == end_x:
        # Vertical segment take first x match
        index = np.searchsorted(x, start_x) - (start_x not in x)
    else:
        # Otherwise non-vertical segment, take last match
        index = np.searchsorted(x, start_x, side="right") - 1

    return n[index]
