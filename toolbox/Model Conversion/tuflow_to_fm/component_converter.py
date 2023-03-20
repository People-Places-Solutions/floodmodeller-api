from floodmodeller_api import XML2D

from typing import TypeVar, Type

from shapely.geometry import LineString, Polygon

T = TypeVar("T")


class ComponentConverter:
    def convert():
        raise NotImplementedError()


class DomainConverter2D(ComponentConverter):
    def __init__(
        self,
        # xml: XML2D,
        xll: float,
        yll: float,
        dx: float,
        nrows: int,
        ncols: int,
        rotation: float = None,
        # active_area: Polygon = None,
    ) -> None:
        # self.xml = xml
        self.xll = xll
        self.yll = yll
        self.dx = dx
        self.nrows = nrows
        self.ncols = ncols
        # self.active_area = active_area
        self.rotation = rotation

    def convert(self) -> None:
        pass

    @classmethod
    def from_loc_line(
        cls: Type[T], loc_line: LineString, dx: float, nx: int, ny: int
    ) -> T:
        x1, y1 = loc_line.coords[0]
        x2, y2 = loc_line.coords[1]

        return cls(xll=x1, yll=y1, dx=dx, nrows=int(nx / dx), ncols=int(ny / dx))
