from floodmodeller_api import XML2D

from pathlib import Path
from shapely.geometry import LineString
import geopandas as gpd
import math


class ComponentConverter:
    def convert(self):
        self._preprocess_settings()
        self._update_file()

    def _preprocess_settings(self):
        raise NotImplementedError()

    def _update_file(self):
        raise NotImplementedError()


class ComputationalAreaConverter(ComponentConverter):

    _xll: float
    _yll: float
    _dx: float
    _nrows: int
    _ncols: int
    _active_area: Path
    _deactive_area: Path
    _rotation: int

    def __init__(self, xml: XML2D, inputs_folder: Path, domain_name: str) -> None:
        self._xml = xml
        self._inputs_folder = inputs_folder
        self._domain_name = domain_name

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
        inputs_folder: Path,
        domain_name: str,
        loc_line: LineString,
        dx: float,
        nx: int,
        ny: int,
        active_area: gpd.GeoDataFrame,
        deactive_area: gpd.GeoDataFrame,
    ) -> None:
        super().__init__(xml, inputs_folder, domain_name)

        self._loc_line = loc_line
        self._dx = dx
        self._nx = nx
        self._ny = ny
        self._active_area = Path.joinpath(inputs_folder, "active_area.shp")
        self._deactive_area = Path.joinpath(inputs_folder, "deactive_area.shp")
        active_area.to_file(self._active_area)
        deactive_area.to_file(self._deactive_area)

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
