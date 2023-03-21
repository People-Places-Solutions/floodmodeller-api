from floodmodeller_api import XML2D

from pathlib import Path
from typing import Union
from shapely.geometry import LineString
import math


class ComponentConverter:
    def __init__(self, inputs_folder: Path) -> None:
        self._inputs_folder = inputs_folder
        self._inputs_folder.mkdir(parents=True, exist_ok=True)

    def convert(self):
        self._transform_settings()
        self._update_file()

    def _transform_settings(self):
        raise NotImplementedError()

    def _update_file(self):
        raise NotImplementedError()


class ComputationalArea2DConverter(ComponentConverter):
    def __init__(self, xml: XML2D, inputs_folder: Path, domain_name: str) -> None:
        super().__init__(inputs_folder)
        self._xml = xml
        self._domain_name = domain_name

    def _update_file(self) -> None:
        self._xml.domains[self._domain_name]["computational_area"] = {
            "xll": self._xll,
            "yll": self._yll,
            "dx": self._dx,
            "nrows": self._nrows,
            "ncols": self._ncols,
            "active_area": self._active_area,
            "rotation": self._rotation,
        }
        self._xml.update()


class LocLineConverter(ComputationalArea2DConverter):
    def __init__(
        self,
        xml: XML2D,
        inputs_folder: Path,
        domain_name: str,
        loc_line: LineString,
        dx: float,
        nx: int,
        ny: int,
        active_area: Union[str, Path],
    ) -> None:
        super().__init__(xml, inputs_folder, domain_name)

        self._loc_line = loc_line
        self._dx = dx
        self._nx = nx
        self._ny = ny
        self._active_area = active_area

    def _transform_settings(self) -> None:
        x1, y1 = self._loc_line.coords[0]
        x2, y2 = self._loc_line.coords[1]
        self._xll = x1
        self._yll = y1
        self._nrows = int(self._nx / self._dx)
        self._ncols = int(self._ny / self._dx)

        theta_rad = math.atan2(y2 - y1, x2 - x1)
        if theta_rad < 0:
            theta_rad += 2 * math.pi
        self._rotation = math.degrees(theta_rad)
