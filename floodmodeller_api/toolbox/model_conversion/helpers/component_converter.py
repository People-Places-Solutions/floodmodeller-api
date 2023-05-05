from floodmodeller_api import XML2D

from pathlib import Path
from shapely.geometry import LineString
from shapely.ops import split
from typing import List, Tuple
import geopandas as gpd
import pandas as pd
import math


def concat(
    gdf_list: List[gpd.GeoDataFrame], mapper: dict = None, lower_case: bool = False
) -> gpd.GeoDataFrame:

    if lower_case:
        gdf_list = [x.rename(columns=str.lower) for x in gdf_list]

    if mapper:
        gdf_list = [x.rename(columns=mapper) for x in gdf_list]

    return gpd.GeoDataFrame(pd.concat(gdf_list, ignore_index=True))


def rename_and_select(df: pd.DataFrame, mapper: dict) -> pd.DataFrame:
    mapper_subset = {k: v for k, v in mapper.items() if k in df.columns}
    return df.rename(columns=mapper_subset)[mapper_subset.values()]


def filter(gdf: gpd.GeoDataFrame, column: str, value: int) -> gpd.GeoDataFrame:
    return gdf[gdf[column] == value].drop(columns=column)


class ComponentConverter:
    def __init__(self, folder: Path) -> None:
        self._folder = folder

    def edit_fm_file(self) -> None:
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
        lx_ly: Tuple[float],
        all_areas: List[gpd.GeoDataFrame],
    ) -> None:

        super().__init__(xml, folder, domain_name)

        self._dx = dx
        self._nrows = int(lx_ly[0] / self._dx)
        self._ncols = int(lx_ly[1] / self._dx)
        self._active_area_path = Path.joinpath(folder, "active_area.shp")
        self._deactive_area_path = Path.joinpath(folder, "deactive_area.shp")

        all_areas_concat = concat(all_areas, lower_case=True)
        filter(all_areas_concat, "code", 0).to_file(self._deactive_area_path)
        filter(all_areas_concat, "code", 1).to_file(self._active_area_path)

    def edit_fm_file(self) -> None:
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
        self._rotation = round(math.degrees(theta_rad), 3)


class TopographyConverter(ComponentConverter2D):
    def __init__(
        self,
        xml: XML2D,
        folder: Path,
        domain_name: str,
        rasters: List[Path],
        vectors: List[Tuple[gpd.GeoDataFrame]],
    ) -> None:
        super().__init__(xml, folder, domain_name)

        self._raster_paths = [str(x) for x in rasters]

        self._vector_paths = []
        for i, value in enumerate(vectors):
            vector_path = str(Path.joinpath(folder, f"topography_{i}.shp"))
            self._vector_paths.append(vector_path)
            self.combine_layers(value).to_file(vector_path)

    def edit_fm_file(self) -> None:
        self._xml.domains[self._domain_name]["topography"] = (
            self._raster_paths + self._vector_paths
        )

    @staticmethod
    def combine_layers(layers: Tuple[gpd.GeoDataFrame]) -> gpd.GeoDataFrame:

        # separate into lines & points
        lines_points = concat(
            layers,
            mapper={"shape_widt": "width", "shape_opti": "options"},
            lower_case=True,
        )
        lines = lines_points[lines_points.geometry.geometry.type == "LineString"]
        points = lines_points[lines_points.geometry.geometry.type == "Point"]

        # split lines according to points
        segments = gpd.GeoDataFrame(
            list(split(lines.geometry.unary_union, points.geometry.unary_union).geoms),
            crs=lines_points.crs,
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
            .sjoin(
                rename_and_select(lines, {"width": "thick", "geometry": "geometry"}),
                how="inner",
                predicate="within",
            )
            .drop(columns="index_right")
            .astype({"height1": float, "height2": float, "thick": float})
        )

        return segments


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
        self._mapping = self.standardise_mapping(mapping)
        self._global_value = self._mapping.loc[
            self._mapping["material_id"] == global_material, "value"
        ][0]

        self._file_material_path = Path.joinpath(folder, "roughness.shp")

        roughness = self.material_to_roughness(file_material, self._mapping)
        roughness.to_file(self._file_material_path)

    @staticmethod
    def standardise_mapping(file: pd.DataFrame) -> pd.DataFrame:
        new_file = file.iloc[:, :2]
        new_file.columns = ["material_id", "value"]
        return new_file

    @staticmethod
    def material_to_roughness(
        material: List[gpd.GeoDataFrame], mapping: pd.DataFrame
    ) -> gpd.GeoDataFrame:
        return (
            concat(material, lower_case=True)
            .merge(mapping, left_on="material", right_on="material_id")[
                ["value", "geometry"]
            ]
        )

    def edit_fm_file(self) -> None:
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

    def edit_fm_file(self) -> None:
        self._xml.domains[self._domain_name]["time"] = {
            "start_offset": self._start_offset,
            "total": self._total,
        }
        self._xml.domains[self._domain_name]["run_data"] = {
            "time_step": self._time_step,
            "scheme": self._scheme,
        }
        self._xml.processor = {"type": self._processor}


class BoundaryConverter(ComponentConverter2D):
    def __init__(
        self,
        xml: XML2D,
        folder: Path,
        domain_name: str,
        vectors: List[gpd.GeoDataFrame],
    ) -> None:
        super().__init__(xml, folder, domain_name)

    def edit_fm_file(self) -> None:
        raise NotImplementedError("Boundary conditions not implemented yet")
