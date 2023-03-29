from typing import List, Tuple
from shapely.ops import split
import geopandas as gpd
import pandas as pd


def concat_geodataframes(
    gdf_list: List[gpd.GeoDataFrame], mapper: dict = None, lower_case: bool = False
) -> gpd.GeoDataFrame:

    if lower_case:
        gdf_list = [x.rename(columns=str.lower) for x in gdf_list]

    if mapper:
        gdf_list = [x.rename(columns=mapper) for x in gdf_list]

    return gpd.GeoDataFrame(pd.concat(gdf_list, ignore_index=True))


def rename_and_select(df: pd.DataFrame, mapper: dict) -> pd.DataFrame:
    return df.rename(columns=mapper)[mapper.values()]


def combine_z_layers(layers: Tuple[gpd.GeoDataFrame]) -> gpd.GeoDataFrame:

    # separate into lines & points
    lines_and_points = concat_geodataframes(
        layers,
        mapper={"shape_widt": "width", "shape_opti": "options"},
        lower_case=True,
    )
    lines = lines_and_points[lines_and_points.geometry.geometry.type == "LineString"]
    points = lines_and_points[lines_and_points.geometry.geometry.type == "Point"]

    # split lines according to points
    segments = gpd.GeoDataFrame(
        split(lines.geometry.unary_union, points.geometry.unary_union),
        crs=lines_and_points.crs,
        columns=["geometry"],
    )

    # get line endpoints
    segments["point1"] = segments.apply(lambda x: x.geometry.boundary.geoms[0], axis=1)
    segments["point2"] = segments.apply(lambda x: x.geometry.boundary.geoms[1], axis=1)

    # get endpoint heights & line thickness
    segments = (
        segments.merge(
            rename_and_select(points, {"z": "height1", "geometry": "point1"}),
            on="point1",
        )
        .drop(columns="point1")
        .merge(
            rename_and_select(points, {"z": "height2", "geometry": "point2"}),
            on="point2",
        )
        .drop(columns="point2")
        .sjoin(
            rename_and_select(lines, {"width": "thick", "geometry": "geometry"}),
            how="inner",
            predicate="within",
        )
        .drop(columns="index_right")
        .astype({"height1": float, "height2": float, "thick": float})
    )

    return segments
