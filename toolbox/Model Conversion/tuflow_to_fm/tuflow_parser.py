from pathlib import Path
from typing import Union
from shapely.geometry.base import BaseGeometry
import geopandas as gpd


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

                self._contents_dict[k] = v

    def _get_raw_value(self, value_name: str) -> str:
        return self._contents_dict[value_name]

    def get_value(self, value_name: str, value_type: type = str) -> object:
        return value_type(self._get_raw_value(value_name))

    def get_list(self, value_name: str, delimiter: str, value_type: type = str) -> list:
        return [value_type(x.strip()) for x in self._get_raw_value(value_name).split(delimiter)]

    def get_tuple(self, value_name: str, delimiter: str, value_type: type = str) -> tuple:
        return tuple(self.get_list(value_name, delimiter, value_type))

    def get_path(self, value_name: str) -> Path:
        return Path.joinpath(self._folder, self._contents_dict[value_name]).resolve()

    def get_geodataframe(self, value_name: str) -> gpd.GeoDataFrame:
        return gpd.read_file(self.get_path(value_name))

    def get_geometry(self, value_name: str) -> BaseGeometry:
        return self.get_geodataframe(value_name).geometry[0]
