from floodmodeller_api import XML2D

from pathlib import Path
from shapely.geometry import LineString
from shapely.ops import split
from typing import List, Tuple
import geopandas as gpd
import pandas as pd
import math


def concat_geodataframes(
    gdf_list: List[gpd.GeoDataFrame], mapper: dict = None, lower_case: bool = False
) -> gpd.GeoDataFrame:

    if lower_case:
        gdf_list = [x.rename(columns=str.lower) for x in gdf_list]

    if mapper:
        gdf_list = [x.rename(columns=mapper) for x in gdf_list]

    return gpd.GeoDataFrame(pd.concat(gdf_list, ignore_index=True))


class ComponentConverter:
    def __init__(self, folder: Path) -> None:
        self._folder = folder

    def update_file(self):
        raise NotImplementedError()


class ComponentConverter2D(ComponentConverter):
    def __init__(self, xml: XML2D, folder: Path, domain_name: str) -> None:
        super().__init__(folder)
        self._xml = xml
        self._domain_name = domain_name


class ComputationalAreaConverter(ComponentConverter2D):

    _xll: float
    _yll: float
    _rotation: int

    def __init__(
        self,
        xml: XML2D,
        folder: Path,
        domain_name: str,
        dx: float,
        lx_ly: tuple,
        all_areas: List[gpd.GeoDataFrame],
    ) -> None:

        super().__init__(xml, folder, domain_name)

        self._dx = dx
        self._nrows = int(lx_ly[0] / self._dx)
        self._ncols = int(lx_ly[1] / self._dx)
        self._active_area_path = Path.joinpath(folder, "active_area.shp")
        self._deactive_area_path = Path.joinpath(folder, "deactive_area.shp")

        all_areas_concat = concat_geodataframes(all_areas, lower_case=True)

        (
            all_areas_concat[all_areas_concat["code"] == 1]
            .drop(columns="code")
            .to_file(self._active_area_path)
        )
        (
            all_areas_concat[all_areas_concat["code"] == 0]
            .drop(columns="code")
            .to_file(self._deactive_area_path)
        )

    def update_file(self) -> None:
        self._xml.domains[self._domain_name]["computational_area"] = {
            "xll": self._xll,
            "yll": self._yll,
            "dx": self._dx,
            "nrows": self._nrows,
            "ncols": self._ncols,
            "active_area": self._active_area_path,
            "deactive_area": self._deactive_area_path,
            "rotation": self._rotation,
        }
        self._xml.update()


class LocLineConverter(ComputationalAreaConverter):
    def __init__(
        self,
        xml: XML2D,
        folder: Path,
        domain_name: str,
        dx: float,
        lx_ly: tuple,
        all_areas: List[gpd.GeoDataFrame],
        loc_line: LineString,
    ) -> None:
        super().__init__(xml, folder, domain_name, dx, lx_ly, all_areas)

        x1, y1 = loc_line.coords[0]
        x2, y2 = loc_line.coords[1]
        self._xll = x1
        self._yll = y1

        theta_rad = math.atan2(y2 - y1, x2 - x1)
        if theta_rad < 0:
            theta_rad += 2 * math.pi
        self._rotation = round(math.degrees(theta_rad))


class TopographyConverter(ComponentConverter2D):
    def __init__(
        self,
        xml: XML2D,
        folder: Path,
        domain_name: str,
        raster: Path,
        shapes: List[Tuple[gpd.GeoDataFrame]],
    ) -> None:
        super().__init__(xml, folder, domain_name)
        self._path = str(raster)
        self._shapes = str(Path.joinpath(folder, "shapes.shp"))

        shapes_concat = concat_geodataframes([self._combine_layers(x) for x in shapes])
        shapes_concat.to_file(self._shapes)

    def update_file(self) -> None:
        self._xml.domains[self._domain_name]["topography"] = [
            self._path,
            self._shapes,
        ]
        self._xml.update()

    def _combine_layers(self, layers: Tuple[gpd.GeoDataFrame]) -> gpd.GeoDataFrame:

        gpd_concat = concat_geodataframes(
            layers,
            mapper={"shape_widt": "thick", "shape_opti": "options"},
            lower_case=True,
        )

        lines = gpd_concat[gpd_concat.geometry.geometry.type == "LineString"]
        line_widths = lines.rename({"width": "thick"})[["thick", "geometry"]]

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

        gdf_segments = (
            line_widths.sjoin(gdf_segments, how="inner", predicate="covers")
            .set_index("index_right")
            .sort_index()
        )
        gdf_segments.index.name = None

        print(gdf_segments)

        return gdf_segments


class RoughnessConverter(ComponentConverter2D):
    def __init__(
        self,
        xml: XML2D,
        folder: Path,
        domain_name: str,
        law: str,
        global_material: int,
        file_material: List[gpd.GeoDataFrame],
        mapping: pd.DataFrame,
    ) -> None:
        super().__init__(xml, folder, domain_name)
        self._law = law
        self._global_value = mapping.loc[
            mapping["Material ID"] == global_material, "Manning's n"
        ][0]

        self._file_material_path = Path.joinpath(folder, "roughness.shp")

        (
            concat_geodataframes(file_material, lower_case=True)
            .merge(mapping, left_on="material", right_on="Material ID")[
                ["Manning's n", "geometry"]
            ]
            .rename(columns={"Manning's n": "value"})
            .to_file(self._file_material_path)
        )

    def update_file(self) -> None:
        self._xml.domains[self._domain_name]["roughness"] = [
            {
                "type": "global",
                "law": self._law,
                "value": self._global_value,
            },
            {
                "type": "file",
                "law": self._law,
                "value": self._file_material_path,
            },
        ]
        self._xml.update()


class SchemeConverter(ComponentConverter2D):
    def __init__(
        self,
        xml: XML2D,
        folder: Path,
        domain_name: str,
        time_step: float,
        start_offset: float,
        total: float,
        scheme: str,
        hardware: str,
    ) -> None:
        super().__init__(xml, folder, domain_name)
        self._time_step = time_step
        self._start_offset = start_offset
        self._total = total

        use_tvd_gpu = scheme == "HPC" and hardware == "GPU"
        self._scheme = "TVD" if use_tvd_gpu else "ADI"
        self._processor = "GPU" if use_tvd_gpu else "CPU"

    def update_file(self) -> None:
        self._xml.domains[self._domain_name]["time"] = {
            "start_offset": self._start_offset,
            "total": self._total,
        }
        self._xml.domains[self._domain_name]["run_data"] = {
            "time_step": self._time_step,
            "scheme": self._scheme,
        }
        self._xml.processor = {"type": self._processor}
        self._xml.update()
