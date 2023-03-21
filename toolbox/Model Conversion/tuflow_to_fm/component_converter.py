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
        xml.domains[domain_name]["computational_area"] = {
            "xll": xll,
            "yll": yll,
            "dx": dx,
            "nrows": nrows,
            "ncols": ncols,
            # "active_area": active_area,
            "rotation": rotation,
        }

    def convert(self) -> None:
        pass

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
        theta_deg = math.degrees(theta_rad)

        return cls(
            xml=xml,
            domain_name=domain_name,
            xll=x1,
            yll=y1,
            dx=dx,
            nrows=int(nx / dx),
            ncols=int(ny / dx),
            rotation=theta_deg,
        )
