from pathlib import Path
from typing import Union, List, Tuple
from shapely.geometry.base import BaseGeometry
from shapely.ops import split
import geopandas as gpd
import pandas as pd


class TuflowParser:
    def __init__(self, file: Union[str, Path]) -> None:

        self._folder = Path(file).parents[0]

        self._dict = {}

        with open(file) as f:

            for line in f:

                line = line.partition("!")[0]

                if line.isspace() or not line:
                    continue

                k, v = line.split("==")

                k = k.strip()
                v = v.strip()

                if k not in self._dict:
                    self._dict[k] = [v]
                else:
                    self._dict[k].append(v)

    def _resolve_path(self, relative_path: Path) -> Path:
        return Path.joinpath(self._folder, relative_path).resolve()

    def get_value(self, name: str, cast: type = str, index: int = -1) -> object:
        return cast(self._dict[name][index])

    def get_tuple(
        self, name: str, sep: str, cast: type = str, index: int = -1
    ) -> tuple:
        return tuple([cast(x.strip()) for x in self._dict[name][index].split(sep)])

    def get_path(self, name: str, index: int = -1) -> Path:
        return self._resolve_path(self._dict[name][index])

    def get_geodataframe(self, name: str, index: int = -1) -> gpd.GeoDataFrame:
        return gpd.read_file(self.get_path(name, index))

    def get_dataframe(self, name: str, index: int = -1) -> pd.DataFrame:
        return pd.read_csv(self.get_path(name, index), comment="!")

    def get_single_geometry(
        self, name: str, index: int = -1, geom_index: int = 0
    ) -> BaseGeometry:
        return self.get_geodataframe(name, index).geometry[geom_index]

    def get_all_geodataframes(
        self, name: str
    ) -> List[Tuple[gpd.GeoDataFrame] | gpd.GeoDataFrame]:

        gdf_list = []

        for i, string in enumerate(self._dict[name]):
            if "|" in string:
                to_append = tuple(
                    [
                        gpd.read_file(self._resolve_path(x))
                        for x in self.get_tuple(name, "|", index=i)
                    ]
                )
            else:
                to_append = gpd.read_file(self._resolve_path(string))

            gdf_list.append(to_append)

        return gdf_list


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
    segments["point1"] = segments.apply(
        lambda x: x.geometry.boundary.geoms[0], axis=1
    )
    segments["point2"] = segments.apply(
        lambda x: x.geometry.boundary.geoms[1], axis=1
    )

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
