from floodmodeller_api import XML2D
from tuflow_parser import TuflowParser
from component_converter import LocLineConverter

from pathlib import Path
from typing import Union
import logging


class ModelConverter:

    _cc_dict: dict

    def __init__(self, log_file: Union[str, Path]) -> None:

        logging.basicConfig(
            filename=log_file,
            filemode="w",
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%H:%M:%S",
            level=logging.INFO,
        )
        self._logger = logging.getLogger("model_converter")

    def convert_model(self):
        for k, v in self._cc_dict.items():
            self._convert_one_component(k, v)

    def _convert_one_component(
        self,
        cc_class_display_name: str,
        cc_subclasses: dict,
    ):
        self._logger.info(f"start converting {cc_class_display_name}")

        for cc_subclass_display_name, cc_factory in cc_subclasses.items():

            self._logger.info(f"trying {cc_subclass_display_name}")

            try:
                cc = cc_factory()
            except:
                # self._logger.error("settings not valid")
                # self._logger.debug("", exc_info=True)
                self._logger.exception("settings not valid")
                continue

            self._logger.info("settings valid")

            try:
                cc.convert()
            except:
                # self._logger.error("conversion failure")
                # self._logger.debug("", exc_info=True)
                self._logger.exception("conversion failure")
                break

            self._logger.info("conversion success")
            self._logger.info(f"end converting {cc_class_display_name}")
            return

        self._logger.info(f"failure converting {cc_class_display_name}")


class ModelConverter2D(ModelConverter):
    def __init__(self, xml_path: Union[str, Path], log_file: Union[str, Path]) -> None:

        super().__init__(log_file)

        self._xml = XML2D()
        self._xml.save(xml_path)

        xml_folder = Path(xml_path).parents[0]
        self._inputs_folder = Path.joinpath(xml_folder, "processed_inputs")
        self._inputs_folder.mkdir(parents=True, exist_ok=True)


class TuflowModelConverter2D(ModelConverter2D):

    _TCF_FILE_NAMES = {
        "tgc": "Geometry Control File",
        "tbc": "BC Control File",
        "ecf": "ESTRY Control File",
    }

    def __init__(
        self,
        tcf_path: Union[str, Path],
        xml_path: Union[str, Path],
        log_file: Union[str, Path],
    ) -> None:

        super().__init__(xml_path, log_file)

        self._tcf = TuflowParser(tcf_path)
        for k, v in self._TCF_FILE_NAMES.items():
            path = self._tcf.get_path(v)
            setattr(self, f"_{k}", TuflowParser(path))

        self._cc_dict = {
            "computational area": {"loc line": self._create_loc_line_cc},
            "COMPUTATIONAL AREA": {"LOC LINE": self._create_loc_line_cc},
        }

    def _create_loc_line_cc(self):

        xml = self._xml
        inputs_folder = self._inputs_folder
        domain_name = "Domain 1"
        loc_line = self._tgc.get_single_geometry("Read GIS Location")
        dx = self._tgc.get_value("Cell Size", float)
        nx, ny = self._tgc.get_tuple("Grid Size (X,Y)", ",", int)

        all_areas = self._tgc.get_all_geodataframes(
            "Read GIS Code", case_insensitive=True
        )
        active_area = all_areas[all_areas["code"] == 1].drop(columns="code")
        deactive_area = all_areas[all_areas["code"] == 0].drop(columns="code")

        cc = LocLineConverter(
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

        return cc
