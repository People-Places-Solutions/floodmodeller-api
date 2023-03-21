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

    def _get_raw_value(self, value_name: str, index: int = -1) -> str:
        return self._contents_dict[value_name][index]

    def _resolve_path(self, relative_path: Path) -> Path:
        return Path.joinpath(self._folder, relative_path).resolve()

    def get_final_value(self, value_name: str, value_type: type = str) -> object:
        return value_type(self._get_raw_value(value_name))

    def get_final_list(self, value_name: str, delimiter: str, value_type: type = str) -> list:
        return [value_type(x.strip()) for x in self._get_raw_value(value_name).split(delimiter)]

    def get_final_tuple(self, value_name: str, delimiter: str, value_type: type = str) -> tuple:
        return tuple(self.get_final_list(value_name, delimiter, value_type))

    def get_final_path(self, value_name: str) -> Path:
        return self._resolve_path(self._get_raw_value(value_name))

    def get_final_geodataframe(self, value_name: str) -> gpd.GeoDataFrame:
        return gpd.read_file(self.get_final_path(value_name))

    def get_final_single_geometry(self, value_name: str, index: int = 0) -> BaseGeometry:
        return self.get_final_geodataframe(value_name).geometry[index]

    def get_final_geodataframe_tuple(self, value_name: str) -> gpd.GeoDataFrame:
        gpd_tuple = (gpd.read_file(self._resolve_path(x)) for x in self.get_final_tuple(value_name, "|"))
        gpd_concat = gpd.GeoDataFrame(pd.concat(gpd_tuple, ignore_index=True))
        return gpd_concat

    def combine_all_geodataframes(self, value_name: str) -> gpd.GeoDataFrame:
        # ["gis\2d_zsh_EG00_Rd_Crest_001_L.shp | gis\2d_zsh_EG00_Rd_Crest_001_P.shp", "gis\2d_zsh_EG14_001_L.shp | gis\2d_zsh_EG14_001_P.shp"]
        # [("gis\2d_zsh_EG00_Rd_Crest_001_L.shp", "gis\2d_zsh_EG00_Rd_Crest_001_P.shp"), ("gis\2d_zsh_EG14_001_L.shp", "gis\2d_zsh_EG14_001_P.shp")]
        # ["gis\2d_zsh_EG00_Rd_Crest_001", "gis\2d_zsh_EG14_001"]
        # Potentially calls itself recursively
        pass