from floodmodeller_api import XML2D

from typing import TypeVar, Type
from shapely.geometry import LineString, Polygon

import math

T = TypeVar("T")


class ComponentConverter:
    def convert():
        raise NotImplementedError()


class DomainConverter2D(ComponentConverter):
    def __init__(
        self,
        xml: XML2D,
        domain_name: str,
        xll: float,
        yll: float,
        dx: float,
        nrows: int,
        ncols: int,
        # active_area: Polygon,
        rotation: float,
    ) -> None:
        self._xml = xml
        self._domain_name = domain_name
        self._xll = xll
        self._yll = yll
        self._dx = dx
        self._nrows = nrows
        self._ncols = ncols
        # self._active_area = active_area
        self._rotation = rotation

    def convert(self) -> None:
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

    @classmethod
    def from_loc_line(
        cls: Type[T],
        xml: XML2D,
        domain_name: str,
        loc_line: LineString,
        dx: float,
        nx: int,
        ny: int,
    ) -> T:

        x1, y1 = loc_line.coords[0]
        x2, y2 = loc_line.coords[1]

        theta_rad = math.atan2(y2 - y1, x2 - x1)
        if theta_rad < 0:
            theta_rad += 2 * math.pi

        return cls(
            xml=xml,
            domain_name=domain_name,
            xll=x1,
            yll=y1,
            dx=dx,
            nrows=int(nx / dx),
            ncols=int(ny / dx),
            rotation=math.degrees(theta_rad),
        )
