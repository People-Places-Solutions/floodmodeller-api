from pathlib import Path
from typing import Union
from shapely.geometry.base import BaseGeometry
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

    def _get_raw_value(self, value_name: str, index: int) -> str:
        return self._contents_dict[value_name][index]

    def _get_list_length(self, value_name: str) -> int:
        return len(self._contents_dict[value_name])

    def _resolve_path(self, relative_path: Path) -> Path:
        return Path.joinpath(self._folder, relative_path).resolve()

    def _concat_geodataframe_tuple(self, gdb_paths: tuple, lower_case: bool) -> gpd.GeoDataFrame:
        gpd_tuple = (gpd.read_file(self._resolve_path(x)) for x in gdb_paths)
        if lower_case:
            gpd_tuple = (x.rename(columns=str.lower) for x in gpd_tuple)
        gpd_concat = gpd.GeoDataFrame(pd.concat(gpd_tuple, ignore_index=True))
        return gpd_concat

    def get_value(self, value_name: str, value_type: type = str, index: int = -1) -> object:
        return value_type(self._get_raw_value(value_name, index))

    def get_list(self, value_name: str, delimiter: str, value_type: type = str, index: int = -1) -> list:
        return [value_type(x.strip()) for x in self._get_raw_value(value_name, index).split(delimiter)]

    def get_tuple(self, value_name: str, delimiter: str, value_type: type = str, index: int = -1) -> tuple:
        return tuple(self.get_list(value_name, delimiter, value_type, index))

    def get_path(self, value_name: str, index: int = -1) -> Path:
        return self._resolve_path(self._get_raw_value(value_name, index))

    def get_geodataframe(self, value_name: str, index: int = -1) -> gpd.GeoDataFrame:
        return gpd.read_file(self.get_path(value_name, index))

    def get_single_geometry(self, value_name: str, geometry_index: int = 0, index: int = -1) -> BaseGeometry:
        return self.get_geodataframe(value_name, index).geometry[geometry_index]

    def get_geodataframe_tuple(self, value_name: str, index: int = -1, lower_case: bool = False) -> gpd.GeoDataFrame:
        return self._concat_geodataframe_tuple(self.get_tuple(value_name, "|", index=index), lower_case)

    def combine_all_geodataframes(self, value_name: str, lower_case: bool = False) -> gpd.GeoDataFrame:
        list_length = self._get_list_length(value_name)
        gpd_list = [self._concat_geodataframe_tuple(self.get_tuple(value_name, "|", index=i), lower_case) for i in range(list_length)]
        gpd_concat = gpd.GeoDataFrame(pd.concat(gpd_list, ignore_index=True))
        return gpd_concat