from pathlib import Path
from typing import Union, List, Tuple
from shapely.geometry.base import BaseGeometry
import geopandas as gpd
import pandas as pd


class FileParser:

    _dict: dict

    def __init__(
        self,
        file: Union[str, Path],
        assignment_symbol: str,
        comment_symbol: str,
        tuple_symbol: str,
    ) -> None:
        self._folder = Path(file).parents[0]
        self._assignment_symbol = assignment_symbol
        self._comment_symbol = comment_symbol
        self._tuple_symbol = tuple_symbol

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
        header = True if filepath.suffix == ".csv" else False
        return pd.read_csv(filepath, comment=self._comment_symbol, header=header)

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
            if self._tuple_symbol in string:
                to_append = tuple(
                    [
                        gpd.read_file(self._resolve_path(x))
                        for x in self.get_tuple(name, self._tuple_symbol, index=i)
                    ]
                )
            else:
                to_append = gpd.read_file(self._resolve_path(string))

            gdf_list.append(to_append)

        return gdf_list


class TuflowParser(FileParser):
    def __init__(self, file: Union[str, Path]) -> None:

        super().__init__(
            file, assignment_symbol="==", comment_symbol="!", tuple_symbol="|"
        )

        self._dict = {}

        with open(file) as f:

            for line in f:

                line = line.partition(self._comment_symbol)[0]

                if line.isspace() or not line:
                    continue

                k, v = line.split(self._assignment_symbol)

                k = k.strip()
                v = v.strip()

                if k not in self._dict:
                    self._dict[k] = [v]
                else:
                    self._dict[k].append(v)
