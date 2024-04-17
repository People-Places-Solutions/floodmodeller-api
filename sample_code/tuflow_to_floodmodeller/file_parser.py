from pathlib import Path
from typing import Dict, List, Literal, Tuple, Type, TypeVar, Union, overload

import geopandas as gpd
import pandas as pd
from shapely.geometry.base import BaseGeometry

T = TypeVar("T", int, float)


class TuflowParser:
    ASSIGNMENT_SYMBOL = "=="
    COMMENT_SYMBOL = "!"
    TUPLE_SYMBOL = "|"

    def __init__(self, file: Union[str, Path]) -> None:
        self._folder = Path(file).parents[0]
        self._dict: Dict[str, List[str]] = {}

        with open(file) as f:
            for line in f:
                line = line.partition(self.COMMENT_SYMBOL)[0]

                if line.isspace() or not line:
                    continue

                if self.ASSIGNMENT_SYMBOL not in line:
                    continue

                k, v = line.split(self.ASSIGNMENT_SYMBOL)

                k = k.strip().lower()
                v = v.strip()

                if k not in self._dict:
                    self._dict[k] = [v]
                else:
                    self._dict[k].append(v)

    def _resolve_path(self, relative_path: str) -> Path:
        return Path.joinpath(self._folder, relative_path).resolve()

    def check_key(self, name: str) -> bool:
        return name in self._dict

    @overload
    def get_value(self, name: str, index: int = -1) -> str: ...

    @overload
    def get_value(self, name: str, cast: Type[T], index: int = -1) -> T: ...

    def get_value(self, name, cast=str, index=-1):
        return cast(self._dict[name][index])

    @overload
    def get_tuple(self, name: str, sep: str, index: int = -1) -> Tuple[str, ...]: ...

    @overload
    def get_tuple(self, name: str, sep: str, cast: Type[T], index: int = -1) -> Tuple[T, ...]: ...

    def get_tuple(self, name, sep, cast=str, index=-1):
        return tuple([cast(x.strip()) for x in self._dict[name][index].split(sep)])

    def get_path(self, name: str, index: int = -1) -> Path:
        return self._resolve_path(self._dict[name][index])

    def get_geodataframe(self, name: str, index: int = -1) -> gpd.GeoDataFrame:
        return gpd.read_file(self.get_path(name, index))

    def get_dataframe(self, name: str, index: int = -1) -> pd.DataFrame:
        filepath = self.get_path(name, index)
        infer: Literal["infer"] = "infer"  # for mypy
        header = infer if filepath.suffix == ".csv" else None
        return pd.read_csv(filepath, comment=self.COMMENT_SYMBOL, header=header)

    def get_single_geometry(self, name: str, index: int = -1, geom_index: int = 0) -> BaseGeometry:
        return self.get_geodataframe(name, index).geometry[geom_index]

    def get_all_paths(self, name: str) -> List[Path]:
        return [self._resolve_path(x) for x in self._dict[name]]

    def get_all_geodataframes(
        self,
        name: str,
    ) -> List[Union[Tuple[gpd.GeoDataFrame], gpd.GeoDataFrame]]:
        gdf_list = []

        for i, string in enumerate(self._dict[name]):
            if self.TUPLE_SYMBOL in string:
                to_append = tuple(
                    [
                        gpd.read_file(self._resolve_path(x))
                        for x in self.get_tuple(name, self.TUPLE_SYMBOL, index=i)
                    ],
                )
            else:
                to_append = gpd.read_file(self._resolve_path(string))

            gdf_list.append(to_append)

        return gdf_list
