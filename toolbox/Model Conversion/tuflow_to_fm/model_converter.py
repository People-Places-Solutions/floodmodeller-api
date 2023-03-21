from floodmodeller_api import XML2D
from tuflow_parser import TuflowParser
from component_converter import DomainConverter2D

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
                print("Failure")


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
            path = self._tcf.get_full_path(v)
            setattr(self, f"_{k}", TuflowParser(path))

        self._component_converters["domain"] = DomainConverter2D.from_loc_line(
            xml=self._xml,
            domain_name="Domain 1",
            loc_line_path=self._tgc.get_full_path("Read GIS Location"),
            dx=float(self._tgc.get_raw_value("Cell Size")),
            nx=int(self._tgc.get_raw_value("Grid Size (X,Y)").split(",")[0]),
            ny=int(self._tgc.get_raw_value("Grid Size (X,Y)").split(",")[1]),
        )
