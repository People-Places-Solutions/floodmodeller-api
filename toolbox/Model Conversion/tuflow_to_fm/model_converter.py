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

        xml_folder = Path(xml_path).parents[0]
        self._inputs_folder = Path.joinpath(xml_folder, "processed_inputs")
        self._inputs_folder.mkdir(parents=True, exist_ok=True)


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
            path = self._tcf.get_final_path(v)
            setattr(self, f"_{k}", TuflowParser(path))

        print(self._tgc.get_final_geodataframe_tuple("Read GIS Z Shape"))

        self._component_converters["computational_area"] = LocLineConverter(
            xml=self._xml,
            inputs_folder=self._inputs_folder,
            domain_name="Domain 1",
            loc_line=self._tgc.get_final_single_geometry("Read GIS Location"),
            dx=self._tgc.get_final_value("Cell Size", float),
            nx=self._tgc.get_final_tuple("Grid Size (X,Y)", ",", int)[0],
            ny=self._tgc.get_final_tuple("Grid Size (X,Y)", ",", int)[1],
            active_area=self._tgc.get_final_geodataframe("Read GIS Code"),
        )
