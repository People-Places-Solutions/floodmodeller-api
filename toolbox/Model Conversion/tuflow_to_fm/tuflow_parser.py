from pathlib import Path
from typing import Union
from shapely.geometry.base import BaseGeometry
from shapely.ops import split
import geopandas as gpd
import pandas as pd


class TuflowParser:
    def __init__(self, file: Union[str, Path]) -> None:

        self._folder = Path(file).parents[0]

        self._contents_dict = {}

        with open(file) as f:

            for line in f:

                line = line.partition("!")[0]

                if line.isspace() or not line:
                    continue

                k, v = line.split("==")

                k = k.strip()
                v = v.strip()

                if k not in self._contents_dict:
                    self._contents_dict[k] = [v]
                else:
                    self._contents_dict[k].append(v)

    def _resolve_path(self, relative_path: Path) -> Path:
        return Path.joinpath(self._folder, relative_path).resolve()

    def _combine_geodataframe_tuple(self, gdb_paths: tuple, case_insensitive: bool) -> gpd.GeoDataFrame:

        gpd_list = [gpd.read_file(self._resolve_path(x)) for x in gdb_paths]

        if case_insensitive:
            gpd_list = [x.rename(columns=str.lower) for x in gpd_list]

        if len(gpd_list) == 1:
            return gpd_list[0]

        gpd_concat = gpd.GeoDataFrame(pd.concat(gpd_list, ignore_index=True))
        lines = gpd_concat[gpd_concat.geometry.geometry.type == "LineString"]
        points = gpd_concat[gpd_concat.geometry.geometry.type == "Point"]

        gdf_segments = gpd.GeoDataFrame(
            split(lines.geometry.unary_union, points.geometry.unary_union),
            crs=gpd_concat.crs,
            columns=["geometry"],
        )
        gdf_segments["start_pt"] = gdf_segments.apply(
            lambda x: x.geometry.boundary.geoms[0], axis=1
        )
        gdf_segments["end_pt"] = gdf_segments.apply(
            lambda x: x.geometry.boundary.geoms[1], axis=1
        )
        gdf_segments = (
            gdf_segments
            .merge(
                points.rename(columns={"z": "height1", "geometry": "geom1"}),
                left_on="start_pt",
                right_on="geom1",
            )
            .merge(
                points.rename(columns={"z": "height2", "geometry": "geom2"}),
                left_on="end_pt",
                right_on="geom2",
            )
            [["height1", "height2", "geometry"]]
        )

        print(gdf_segments)
        print(gdf_segments.columns)

        return gdf_segments

    def get_value(self, val_name: str, val_type: type = str, index: int = -1) -> object:
        return val_type(self._contents_dict[val_name][index])

    def get_list(self, val_name: str, sep: str, val_type: type = str, index: int = -1) -> list:
        return [val_type(x.strip()) for x in self._contents_dict[val_name][index].split(sep)]

    def get_tuple(self, val_name: str, sep: str, val_type: type = str, index: int = -1) -> tuple:
        return tuple(self.get_list(val_name, sep, val_type, index))

    def get_path(self, val_name: str, index: int = -1) -> Path:
        return self._resolve_path(self._contents_dict[val_name][index])

    def get_geodataframe(self, val_name: str, index: int = -1) -> gpd.GeoDataFrame:
        return gpd.read_file(self.get_path(val_name, index))

    def get_dataframe(self, val_name: str, index: int = -1) -> pd.DataFrame:
        return pd.read_csv(self.get_path(val_name, index))

    def get_single_geometry(self, val_name: str, shp_index: int = 0, list_index: int = -1) -> BaseGeometry:
        return self.get_geodataframe(val_name, list_index).geometry[shp_index]

    def get_geodataframe_tuple(self, val_name: str, index: int = -1, case_insensitive: bool = False) -> gpd.GeoDataFrame:
        return self._combine_geodataframe_tuple(self.get_tuple(val_name, "|", index=index), case_insensitive)

    def get_all_geodataframes(self, val_name: str, case_insensitive: bool = False) -> gpd.GeoDataFrame:
        gpd_path_list_len = len(self._contents_dict[val_name])
        gpd_list = [
            self._combine_geodataframe_tuple(
                self.get_tuple(val_name, "|", index=i), case_insensitive
            )
            for i in range(gpd_path_list_len)
        ]
        gpd_concat = gpd.GeoDataFrame(pd.concat(gpd_list, ignore_index=True))
        return gpd_concat