from floodmodeller_api import XML2D
from file_parser import TuflowParser
from component_converter import (
    LocLineConverter,
    TopographyConverter,
    RoughnessConverter,
    SchemeConverter,
)

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

    def save_file(self):
        raise NotImplementedError()

    def rollback_file(self):
        raise NotImplementedError()

    def convert_model(self):
        for k, v in self._cc_dict.items():
            self._convert_one_component(k, v)

    def _convert_one_component(
        self,
        cc_class_display_name: str,
        cc_factory: callable,
    ):
        self._logger.info(f"converting {cc_class_display_name}...")

        try:
            cc_object = cc_factory()
        except:
            # self._logger.error("settings not valid")
            # self._logger.debug("", exc_info=True)
            self._logger.exception("settings are not valid")
            return

        self._logger.info("settings are valid")

        try:
            cc_object.edit_file()
            self.save_file()
        except:
            # self._logger.error("updating file failure")
            # self._logger.debug("", exc_info=True)
            self._logger.exception("updating file failed")
            self.rollback_file()
            return

        self._logger.info("updating file succeeded")


class ModelConverter2D(ModelConverter):
    def __init__(self, xml_path: Union[str, Path], log_file: Union[str, Path]) -> None:

        super().__init__(log_file)

        self._xml_path = xml_path
        self._xml = XML2D()
        self._xml.save(self._xml_path)

        xml_folder = Path(self._xml_path).parents[0]
        self._folder = Path.joinpath(xml_folder, "processed_inputs")
        self._folder.mkdir(parents=True, exist_ok=True)

    def save_file(self):
        self._xml.update()

    def rollback_file(self):
        self._xml = XML2D(self._xml_path)

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
            "computational area": self._create_computational_area_cc,
            "topography": self._create_topography_cc,
            "roughness": self._create_roughness_cc,
            "scheme": self._create_scheme_cc,
        }

    def _create_computational_area_cc(self):

        return LocLineConverter(
            xml=self._xml,
            folder=self._folder,
            domain_name="Domain 1",
            dx=self._tgc.get_value("Cell Size", float),
            lx_ly=self._tgc.get_tuple("Grid Size (X,Y)", ",", int),
            all_areas=self._tgc.get_all_geodataframes("Read GIS Code"),
            loc_line=self._tgc.get_single_geometry("Read GIS Location"),
        )

    def _create_topography_cc(self):

        return TopographyConverter(
            xml=self._xml,
            folder=self._folder,
            domain_name="Domain 1",
            rasters=self._tgc.get_all_paths("Read GRID Zpts"),
            vectors=self._tgc.get_all_geodataframes("Read GIS Z Shape"),
        )

    def _create_roughness_cc(self):

        return RoughnessConverter(
            xml=self._xml,
            folder=self._folder,
            domain_name="Domain 1",
            law="manning",
            global_material=self._tgc.get_value("Set Mat", int),
            file_material=self._tgc.get_all_geodataframes("Read GIS Mat"),
            mapping=self._tcf.get_dataframe("Read Materials File"),
        )

    def _create_scheme_cc(self):

        return SchemeConverter(
            xml=self._xml,
            folder=self._folder,
            domain_name="Domain 1",
            time_step=self._tcf.get_value("Timestep", float),
            start_offset=self._tcf.get_value("Start Time", float),
            total=self._tcf.get_value("End Time", float),
            scheme=self._tcf.get_value("Solution Scheme"),
            hardware=self._tcf.get_value("Hardware"),
        )
