from floodmodeller_api import XML2D
from tuflow_parser import TuflowParser
from component_converter import LocLineConverter

from pathlib import Path
from typing import Union


class ModelConverter:
    def __init__(self) -> None:
        self._component_converters = {}

    def convert(self):
        for k, v in self._component_converters.items():
            print(f"Converting {k}...")
            try:
                v.convert()
            except Exception as e:
                print(f"Failure ({e})")


class ModelConverter2D(ModelConverter):
    def __init__(self, xml_path: Union[str, Path]) -> None:
        super().__init__()
        self._xml = XML2D()
        self._xml.save(xml_path)


class TuflowModelConverter2D(ModelConverter2D):

    TCF_FILE_NAMES = {
        "tgc": "Geometry Control File",
        "tbc": "BC Control File",
        "ecf": "ESTRY Control File",
    }

    def __init__(self, tcf_path: Union[str, Path], xml_path: Union[str, Path]) -> None:
        super().__init__(xml_path)

        self._tcf = TuflowParser(tcf_path)
        for k, v in self.TCF_FILE_NAMES.items():
            path = self._tcf.get_path(v)
            setattr(self, f"_{k}", TuflowParser(path))

        nx,ny = self._tgc.get_tuple("Grid Size (X,Y)", int)
        self._component_converters["domain"] = LocLineConverter(
            xml=self._xml,
            domain_name="Domain 1",
            loc_line=self._tgc.get_geometry("Read GIS Location"),
            dx=self._tgc.get_value("Cell Size", float),
            nx=nx,
            ny=ny,
            active_area=self._tgc.get_path("Read GIS Code"),
        )