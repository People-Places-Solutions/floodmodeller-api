from pathlib import Path
from typing import Union, List, Tuple
from shapely.geometry.base import BaseGeometry
import geopandas as gpd
import pandas as pd


class TuflowParser:

    ASSIGNMENT_SYMBOL = "=="
    COMMENT_SYMBOL = "!"
    TUPLE_SYMBOL = "|"

    def __init__(
        self,
        file: Union[str, Path],
    ) -> None:

        self._folder = Path(file).parents[0]
        self._dict = {}

        with open(file) as f:

            for line in f:

                line = line.partition(self.COMMENT_SYMBOL)[0]

                if line.isspace() or not line:
                    continue

                k, v = line.split(self.ASSIGNMENT_SYMBOL)

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
        filepath = self.get_path(name, index)
        header = "infer" if filepath.suffix == ".csv" else None
        return pd.read_csv(filepath, comment=self.COMMENT_SYMBOL, header=header)

    def get_single_geometry(
        self, name: str, index: int = -1, geom_index: int = 0
    ) -> BaseGeometry:
        return self.get_geodataframe(name, index).geometry[geom_index]

    def get_all_paths(self, name: str) -> List[Path]:
        return [self._resolve_path(x) for x in self._dict[name]]

    def get_all_geodataframes(
        self, name: str
    ) -> List[Union[Tuple[gpd.GeoDataFrame], gpd.GeoDataFrame]]:

        gdf_list = []

        for i, string in enumerate(self._dict[name]):
            if self.TUPLE_SYMBOL in string:
                to_append = tuple(
                    [
                        gpd.read_file(self._resolve_path(x))
                        for x in self.get_tuple(name, self.TUPLE_SYMBOL, index=i)
                    ]
                )
            else:
                to_append = gpd.read_file(self._resolve_path(string))

            gdf_list.append(to_append)

        return gdf_list
