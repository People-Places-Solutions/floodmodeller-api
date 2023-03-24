from floodmodeller_api import XML2D

from pathlib import Path
from shapely.geometry import LineString
import geopandas as gpd
import math


class ComponentConverter:
    def __init__(self, folder: Path) -> None:
        self._folder = folder

    def convert(self):
        self._preprocess_settings()
        self._update_file()

    def _preprocess_settings(self):
        raise NotImplementedError()

    def _update_file(self):
        raise NotImplementedError()


class ComponentConverter2D(ComponentConverter):
    def __init__(self, xml: XML2D, folder: Path, domain_name: str) -> None:
        super().__init__(folder)
        self._xml = xml
        self._domain_name = domain_name


class ComputationalAreaConverter(ComponentConverter2D):

    _xll: float
    _yll: float
    _dx: float
    _nrows: int
    _ncols: int
    _active_area: Path
    _deactive_area: Path
    _rotation: int

    def _update_file(self) -> None:
        self._xml.domains[self._domain_name]["computational_area"] = {
            "xll": self._xll,
            "yll": self._yll,
            "dx": self._dx,
            "nrows": self._nrows,
            "ncols": self._ncols,
            "active_area": self._active_area,
            "deactive_area": self._deactive_area,
            "rotation": self._rotation,
        }
        self._xml.update()


class LocLineConverter(ComputationalAreaConverter):
    def __init__(
        self,
        xml: XML2D,
        folder: Path,
        domain_name: str,
        loc_line: LineString,
        dx: float,
        nx_ny: tuple,
        all_areas: gpd.GeoDataFrame,
    ) -> None:
        super().__init__(xml, folder, domain_name)

        self._loc_line = loc_line
        self._dx = dx
        self._nx, self._ny = nx_ny
        self._all_areas = all_areas
        self._active_area = Path.joinpath(folder, "active_area.shp")
        self._deactive_area = Path.joinpath(folder, "deactive_area.shp")

    def _preprocess_settings(self) -> None:
        x1, y1 = self._loc_line.coords[0]
        x2, y2 = self._loc_line.coords[1]
        self._xll = x1
        self._yll = y1
        self._nrows = int(self._nx / self._dx)
        self._ncols = int(self._ny / self._dx)

        theta_rad = math.atan2(y2 - y1, x2 - x1)
        if theta_rad < 0:
            theta_rad += 2 * math.pi
        self._rotation = round(math.degrees(theta_rad))

        (
            self
            ._all_areas[self._all_areas["code"] == 1]
            .drop(columns="code")
            .to_file(self._active_area)
        )

        (
            self
            ._all_areas[self._all_areas["code"] == 0]
            .drop(columns="code")
            .to_file(self._deactive_area)
        )


class TopographyConverter(ComponentConverter2D):

    def __init__(
        self, xml: XML2D, folder: Path, domain_name: str, raster: Path
    ) -> None:
        super().__init__(xml, folder, domain_name)
        self._raster = raster

    def _preprocess_settings(self) -> None:
        self._topo_path = str(self._raster)

    def _update_file(self) -> None:
        self._xml.domains[self._domain_name]["topography"] = self._topo_path
        self._xml.update()


# class RoughnessConverter(ComponentConverter2D):

#     def __init__(
#         self, xml: XML2D, folder: Path, domain_name: str, raster: Path
#     ) -> None:
#         super().__init__(xml, folder, domain_name)
#         self._raster = raster

#     def _preprocess_settings(self) -> None:
#         self._type
#         self._law
#         self._value

#     def _update_file(self) -> None:
#         self._xml.domains[self._domain_name]["roughness"] = {
#             "type": self._type,
#             "law": self._law,
#             "value": self._value,
#         }
#         self._xml.update()
