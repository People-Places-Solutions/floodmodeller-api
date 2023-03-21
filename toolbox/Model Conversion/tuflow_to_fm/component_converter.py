from floodmodeller_api import XML2D

from typing import Union
from pathlib import Path
from shapely.geometry import LineString

import geopandas as gpd

import math


class ComponentConverter:
    def convert(self):
        self._transform_settings()
        self._update_file()

    def _transform_settings(self):
        raise NotImplementedError()

    def _update_file(self):
        raise NotImplementedError()


class Domain2DConverter(ComponentConverter):
    def __init__(
        self,
        xml: XML2D,
        domain_name: str,
    ) -> None:
        self._xml = xml
        self._domain_name = domain_name

    def _update_file(self) -> None:
        self._xml.domains[self._domain_name]["computational_area"] = {
            "xll": self._xll,
            "yll": self._yll,
            "dx": self._dx,
            "nrows": self._nrows,
            "ncols": self._ncols,
            # "active_area": self._active_area,
            "rotation": self._rotation,
        }
        self._xml.update()


class LocLineConverter(Domain2DConverter):
    def __init__(
        self,
        xml: XML2D,
        domain_name: str,
        loc_line: LineString,
        dx: float,
        nx: int,
        ny: int,
    ) -> None:
        super().__init__(xml, domain_name)

        self._loc_line = loc_line
        self._dx = dx
        self._nx = nx
        self._ny = ny

    def _transform_settings(self):
        x1, y1 = self._loc_line.coords[0]
        x2, y2 = self._loc_line.coords[1]

        theta_rad = math.atan2(y2 - y1, x2 - x1)
        if theta_rad < 0:
            theta_rad += 2 * math.pi

        self._xll = x1
        self._yll = y1
        self._nrows = int(self._nx / self._dx)
        self._ncols = int(self._ny / self._dx)
        self._rotation = math.degrees(theta_rad)
