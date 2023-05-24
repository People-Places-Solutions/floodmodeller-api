from floodmodeller_api import IEF, XML2D

from pathlib import Path
from shapely.geometry import LineString
from shapely.ops import split
from typing import List, Tuple, Union
import geopandas as gpd
import pandas as pd
import numpy as np
import math


def concat(gdf_list: List[gpd.GeoDataFrame]) -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(pd.concat(gdf_list, ignore_index=True))


def rename_and_select(df: pd.DataFrame, mapper: dict) -> pd.DataFrame:
    mapper_subset = {k: v for k, v in mapper.items() if k in df.columns}
    return df.rename(columns=mapper_subset)[mapper_subset.values()]


def filter(gdf: gpd.GeoDataFrame, column: str, value: int) -> gpd.GeoDataFrame:
    is_selected = gdf.loc[:, column] == value
    is_selected = is_selected[is_selected].index
    return gdf.iloc[is_selected].drop(columns=column)


class ComponentConverter:
    def __init__(self, folder: Path) -> None:
        self._folder = folder


class ComponentConverter1D(ComponentConverter):
    def __init__(self, ief: IEF, folder: Path) -> None:
        super().__init__(folder)
        self._ief = ief

    def edit_ief(self) -> None:
        raise NotImplementedError("Abstract method not overwritten")


class SchemeConverter1D(ComponentConverter1D):
    def __init__(
        self,
        ief: IEF,
        folder: Path,
        time_step: float,
    ) -> None:
        super().__init__(ief, folder)
        self._time_step = time_step

    def edit_ief(self) -> None:
        self._ief.Timestep = self._time_step


class ComponentConverter2D(ComponentConverter):
    def __init__(self, xml: XML2D, folder: Path, domain_name: str) -> None:
        super().__init__(folder)
        self._xml = xml
        self._domain_name = domain_name

    def edit_xml(self) -> None:
        raise NotImplementedError("Abstract method not overwritten")


class ComputationalAreaConverter2D(ComponentConverter2D):

    def __init__(
        self,
        xml: XML2D,
        folder: Path,
        domain_name: str,
        xll: float,
        yll: float,
        dx: float,
        lx_ly: Tuple[float],
        all_areas: List[gpd.GeoDataFrame],
        rotation: float = None,
    ) -> None:

        super().__init__(xml, folder, domain_name)

        self._xll = xll
        self._yll = yll
        self._dx = dx
        self._nrows = int(lx_ly[0] / self._dx)
        self._ncols = int(lx_ly[1] / self._dx)
        self._rotation = rotation

        self._active_area_path = None
        self._deactive_area_path = None

        all_areas_concat = concat([self.standardise_areas(x) for x in all_areas])

        for name, code in {"active": 1, "deactive": 0}.items():
            area = filter(all_areas_concat, "code", code)
            area_exists = len(area.index) > 0
            if area_exists:
                path = Path.joinpath(folder, f"{name}_area.shp")
                setattr(self, f"_{name}_area_path", path)
                area.to_file(path)

    @staticmethod
    def standardise_areas(file: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        new_file = file.iloc[:, :]
        new_file.columns = ["code", "geometry"]
        return new_file

    def edit_xml(self) -> None:

        comp_area_dict = {
            "xll": self._xll,
            "yll": self._yll,
            "dx": self._dx,
            "nrows": self._nrows,
            "ncols": self._ncols,
        }

        if self._rotation:
            comp_area_dict["rotation"] = self._rotation

        if self._active_area_path:
            comp_area_dict["active_area"] = self._active_area_path

        if self._deactive_area_path:
            comp_area_dict["deactive_area"] = self._deactive_area_path

        self._xml.domains[self._domain_name]["computational_area"] = comp_area_dict


class LocLineConverter2D(ComputationalAreaConverter2D):
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
        
        x1, y1 = loc_line.coords[0]
        x2, y2 = loc_line.coords[1]

        super().__init__(xml, folder, domain_name, x1, y1, dx, lx_ly, all_areas)

        theta_rad = math.atan2(y2 - y1, x2 - x1)
        if theta_rad < 0:
            theta_rad += 2 * math.pi
        self._rotation = round(math.degrees(theta_rad), 3)


class TopographyConverter2D(ComponentConverter2D):
    def __init__(
        self,
        xml: XML2D,
        folder: Path,
        domain_name: str,
        rasters: List[Path],
        vectors: List[Union[Tuple[gpd.GeoDataFrame], gpd.GeoDataFrame]],
    ) -> None:
        super().__init__(xml, folder, domain_name)

        self._raster_paths = [str(x) for x in rasters]

        self._vector_paths = []
        for i, value in enumerate(vectors):
            vector_path = str(Path.joinpath(folder, f"topography_{i}.shp"))
            self._vector_paths.append(vector_path)
            if type(value) != tuple:
                value = (value,)
            self.combine_layers(value).to_file(vector_path)

    def edit_xml(self) -> None:
        self._xml.domains[self._domain_name]["topography"] = (
            self._raster_paths + self._vector_paths
        )

    @classmethod
    def combine_layers(cls, layers: Tuple[gpd.GeoDataFrame]) -> gpd.GeoDataFrame:

        all_types = concat([cls.standardise_topography(x) for x in layers])

        lines = all_types[all_types.geometry.geometry.type == "LineString"]
        points = all_types[all_types.geometry.geometry.type == "Point"]
        polygons = all_types[all_types.geometry.geometry.type == "Polygon"]

        lines_present = len(lines.index) > 0
        points_present = len(points.index) > 0
        polygons_present = len(polygons.index) > 0

        if lines_present and points_present and not polygons_present:
            return cls.convert_lines_and_points(lines, points)

        elif polygons_present and not (points_present or lines_present):
            return cls.convert_polygons(polygons)

        else:

            spatial_types = []
            if lines_present:
                spatial_types.append("lines")
            if points_present:
                spatial_types.append("points")
            if polygons_present:
                spatial_types.append("polygons")
            spatial_types_display = ", ".join(spatial_types)

            raise RuntimeError(f"Combination not supported: {spatial_types_display}")

    @staticmethod
    def standardise_topography(file: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        new_file = file.iloc[:, :]
        new_file.columns = ["z", "dz", "width", "options", "geometry"]
        return new_file

    @staticmethod
    def convert_lines_and_points(
        lines: gpd.GeoDataFrame, points: gpd.GeoDataFrame
    ) -> gpd.GeoDataFrame:

        # split lines according to points
        segments = gpd.GeoDataFrame(
            list(split(lines.geometry.unary_union, points.geometry.unary_union).geoms),
            crs=lines.crs,
            columns=["geometry"],
        )

        # get line endpoints
        segments[["point1", "point2"]] = pd.DataFrame(
            segments.apply(lambda x: list(x.geometry.boundary.geoms), axis=1).tolist()
        )
        segments["point1"] = gpd.GeoSeries(segments["point1"])
        segments["point2"] = gpd.GeoSeries(segments["point2"])

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
            .astype({"height1": float, "height2": float})
        )

        return segments

    @staticmethod
    def convert_polygons(polygons: gpd.GeoDataFrame) -> gpd.GeoDataFrame:

        new_polygons = polygons.iloc[:, [0, 3, 4]]
        new_polygons.columns = ["height", "method", "geometry"]

        method_is_add = new_polygons["method"] == "ADD"
        new_polygons.loc[method_is_add, "method"] = "add"
        new_polygons.loc[~method_is_add, "method"] = np.nan

        return new_polygons


class RoughnessConverter2D(ComponentConverter2D):
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
        self._material = concat([self.standardise_material(x) for x in file_material])
        self._mapping = self.standardise_mapping(mapping)

        is_global = self._mapping["material_id"] == global_material
        self._global_value = float(self._mapping.loc[is_global, "value"])

        self._file_material_path = Path.joinpath(folder, "roughness.shp")

        roughness = self.material_to_roughness(self._material, self._mapping)
        roughness.to_file(self._file_material_path)

    @staticmethod
    def standardise_material(file: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        new_file = file.iloc[:, [0, -1]]
        new_file.columns = ["material_id", "geometry"]
        return new_file

    @staticmethod
    def standardise_mapping(file: pd.DataFrame) -> pd.DataFrame:
        new_file = file.iloc[:, :2]
        new_file.columns = ["material_id", "value"]
        return new_file

    @staticmethod
    def material_to_roughness(
        material: gpd.GeoDataFrame, mapping: pd.DataFrame
    ) -> gpd.GeoDataFrame:
        return pd.merge(material, mapping, on="material_id")[["value", "geometry"]]

    def edit_xml(self) -> None:
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


class SchemeConverter2D(ComponentConverter2D):
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

    def edit_xml(self) -> None:
        self._xml.domains[self._domain_name]["time"] = {
            "start_offset": self._start_offset,
            "total": self._total,
        }
        self._xml.domains[self._domain_name]["run_data"] = {
            "time_step": self._time_step,
            "scheme": self._scheme,
        }
        self._xml.processor = {"type": self._processor}


class BoundaryConverter2D(ComponentConverter2D):
    def __init__(
        self,
        xml: XML2D,
        folder: Path,
        domain_name: str,
        vectors: List[gpd.GeoDataFrame],
    ) -> None:
        super().__init__(xml, folder, domain_name)
        # print(vectors)
