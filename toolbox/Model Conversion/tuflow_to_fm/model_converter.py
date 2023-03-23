from floodmodeller_api import XML2D
from tuflow_parser import TuflowParser
from component_converter import LocLineConverter

from pathlib import Path
from typing import Union
import logging


class ModelConverter:
    def __init__(self, log_file: Union[str, Path]) -> None:

        logging.basicConfig(
            filename=log_file,
            filemode="w",
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%H:%M:%S",
            level=logging.INFO,
        )
        self._logger = logging.getLogger("model_converter")

        self._component_converters = {}

    def convert(self):
        for k, v in self._component_converters.items():
            self._logger.info(f"converting [{k}]")
            try:
                v.convert()
                self._logger.info("success")
            except Exception:
                # self._logger.error("failure")
                # self._logger.debug("", exc_info=True)
                self._logger.exception("failure")


class ModelConverter2D(ModelConverter):
    def __init__(self, xml_path: Union[str, Path], log_file: Union[str, Path]) -> None:
        super().__init__(log_file)

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

    LOC_LINE_KEYS = {
        "loc_line": "Read GIS Location",
        "dx": "Cell Size",
        "nx, ny": "Grid Size (X,Y)",
        "all_areas": "Read GIS Code",
    }

    def __init__(
        self,
        tcf_path: Union[str, Path],
        xml_path: Union[str, Path],
        log_file: Union[str, Path],
    ) -> None:
        super().__init__(xml_path, log_file)

        self._tcf = TuflowParser(tcf_path)
        for k, v in self.TCF_FILE_NAMES.items():
            path = self._tcf.get_path(v)
            setattr(self, f"_{k}", TuflowParser(path))

        self._init_computational_area()

    def _init_computational_area(self):

        if not self._tgc.check_names(self.LOC_LINE_KEYS.values()):
            return

        self._logger.info("loc line settings detected")

        xml = self._xml
        inputs_folder = self._inputs_folder
        domain_name = "Domain 1"
        loc_line = self._tgc.get_single_geometry(self.LOC_LINE_KEYS["loc_line"])
        dx = self._tgc.get_value(self.LOC_LINE_KEYS["dx"], float)
        nx, ny = self._tgc.get_tuple(self.LOC_LINE_KEYS["nx, ny"], ",", int)

        all_areas = self._tgc.get_all_geodataframes(self.LOC_LINE_KEYS["all_areas"], lower_case=True)
        active_area = all_areas[all_areas["code"] == 1].drop(columns="code")
        deactive_area = all_areas[all_areas["code"] == 0].drop(columns="code")

        self._component_converters["computational_area"] = LocLineConverter(
            xml=xml,
            inputs_folder=inputs_folder,
            domain_name=domain_name,
            loc_line=loc_line,
            dx=dx,
            nx=nx,
            ny=ny,
            active_area=active_area,
            deactive_area=deactive_area,
        )
