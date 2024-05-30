import numpy as np
import pandas as pd
from shapely import LineString, Polygon, intersection


def calculate_cross_section_conveyance(
    x: np.array, y: np.array, n: np.array, panel_markers: np.array
) -> pd.Series:
    wls = insert_intermediate_wls(np.unique(y), threshold=0.1)
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
    x: np.array, y: np.array, n: np.array, wls: np.array
) -> list[float]:
    x = np.array([x[0], *x, x[-1]])  # insert additional start/end points
    n = np.array([0, *n, 0])
    max_y = np.max(y) + 1
    min_y = np.min(y) - 1
    y = np.array([max_y, *y, max_y])
    channel_polygon = Polygon(zip(x, y))
    start, end = x[0] - 0.1, x[-1] + 0.1
    glass_wall_left = LineString(zip([x[0], x[1]], [y[0], y[1]]))
    glass_wall_right = LineString(zip([x[-2], x[-1]], [y[-2], y[-1]]))

    conveyance_values = []
    for wl in wls:
        water_surface = Polygon(zip([start, start, end, end], [wl, min_y, min_y, wl]))
        water_plane = intersection(channel_polygon, LineString(zip([start, end], [wl, wl])))
        glass_wall_left_clip = intersection(water_surface, glass_wall_left)
        glass_wall_right_clip = intersection(water_surface, glass_wall_right)

        wetted_polygon = intersection(channel_polygon, water_surface)
        area = wetted_polygon.area

        if wetted_polygon.geom_type == "GeometryCollection":
            wetted_polygon_perimeter = sum([p.boundary.length for p in wetted_polygon.geoms])
        else:
            wetted_polygon_perimeter = wetted_polygon.boundary.length

        wetted_perimeter = (
            wetted_polygon_perimeter
            - water_plane.length
            - glass_wall_left_clip.length
            - glass_wall_right_clip.length
        )

        if wetted_perimeter < 1e-8:
            conveyance_values.append(0)
            continue

        # TODO: this needs to be updated to be proper weighted manning calc and RPL
        rpl = 1
        weighted_mannings = np.mean(n[np.where(y < wl)]) * wetted_perimeter * np.sqrt(rpl)

        k = (area ** (5 / 3) / wetted_perimeter ** (2 / 3)) * (wetted_perimeter / weighted_mannings)
        conveyance_values.append(k)

    return conveyance_values


def insert_intermediate_wls(arr, threshold):
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
