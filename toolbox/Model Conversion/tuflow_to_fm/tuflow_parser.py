from pathlib import Path
from typing import Union
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

    def get_list(self, name: str, sep: str, cast: type = str, index: int = -1) -> list:
        return [cast(x.strip()) for x in self._dict[name][index].split(sep)]

    def get_tuple(
        self, name: str, sep: str, cast: type = str, index: int = -1
    ) -> tuple:
        return tuple(self.get_list(name, sep, cast, index))

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

    def _combine_layers(
        self,
        name: str,
        index: int = -1,
        case_insensitive: bool = False,
        remove_prefixes: bool = False,
    ) -> gpd.GeoDataFrame:

        gpd_list = [
            gpd.read_file(self._resolve_path(x))
            for x in self.get_tuple(name, "|", index=index)
        ]

        if remove_prefixes:
            gpd_list = [
                x.rename(columns={"Shape_Widt": "Width", "Shape_Opti": "Options"})
                for x in gpd_list
            ]

        if case_insensitive:
            gpd_list = [x.rename(columns=str.lower) for x in gpd_list]

        if len(gpd_list) == 1:
            return gpd_list[0]

        gpd_concat = gpd.GeoDataFrame(pd.concat(gpd_list, ignore_index=True))

        lines = gpd_concat[gpd_concat.geometry.geometry.type == "LineString"]
        # line_widths = lines[["width", "geometry"]]

        points = gpd_concat[gpd_concat.geometry.geometry.type == "Point"]
        point1 = points.rename(columns={"z": "height1", "geometry": "point1"})[
            ["height1", "point1"]
        ]
        point2 = points.rename(columns={"z": "height2", "geometry": "point2"})[
            ["height2", "point2"]
        ]

        gdf_segments = gpd.GeoDataFrame(
            split(lines.geometry.unary_union, points.geometry.unary_union),
            crs=gpd_concat.crs,
            columns=["geometry"],
        )
        gdf_segments["point1"] = gdf_segments.apply(
            lambda x: x.geometry.boundary.geoms[0], axis=1
        )
        gdf_segments["point2"] = gdf_segments.apply(
            lambda x: x.geometry.boundary.geoms[1], axis=1
        )
        gdf_segments = (
            gdf_segments.merge(point1, on="point1")
            .drop(columns="point1")
            .merge(point2, on="point2")
            .drop(columns="point2")
        )

        print(gdf_segments)
        print(gdf_segments.columns)

        return gdf_segments

    def get_all_geodataframes(
        self,
        name: str,
        case_insensitive: bool = False,
        remove_prefixes: bool = False,
    ) -> gpd.GeoDataFrame:

        gpd_path_list_len = len(self._dict[name])
        gpd_list = [
            self._combine_layers(name, i, case_insensitive, remove_prefixes)
            for i in range(gpd_path_list_len)
        ]
        gpd_concat = gpd.GeoDataFrame(pd.concat(gpd_list, ignore_index=True))

        return gpd_concat
