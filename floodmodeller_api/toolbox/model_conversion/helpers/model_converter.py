from floodmodeller_api import IEF, XML2D
from floodmodeller_api._base import FMFile
from .file_parser import TuflowParser
from .component_converter import (
    LocLineConverter,
    TopographyConverter,
    RoughnessConverter,
    SchemeConverter,
    BoundaryConverter,
)

from pathlib import Path
from typing import Union
import logging


class ModelConverter:

    _cc_dict: dict

    PROCESSED_INPUTS_FOLDER_NAME = "gis"

    def __init__(
        self,
        fm_file_class: FMFile,
        fm_file_path: Union[str, Path],
        log_path: Union[str, Path],
    ) -> None:

        self._fm_file_class = fm_file_class
        self._fm_file_path = fm_file_path

        logging.basicConfig(
            filename=log_path,
            filemode="w",
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%H:%M:%S",
            level=logging.INFO,
        )
        self._logger = logging.getLogger("model_converter")

        self._fm_file = self._fm_file_class()
        self._fm_file.save(self._fm_file_path)

        self._processed_inputs_folder = Path.joinpath(
            Path(self._fm_file_path).parents[0], self.PROCESSED_INPUTS_FOLDER_NAME
        )
        self._processed_inputs_folder.mkdir(parents=True, exist_ok=True)

    def convert_model(self) -> None:

        for cc_class_display_name, cc_factory in self._cc_dict.items():

            self._logger.info(f"converting {cc_class_display_name}...")

            try:
                cc_object = cc_factory()
                cc_object.edit_fm_file()
                self.save_fm_file()
            except:
                self._logger.exception("failure")
                self.rollback_fm_file()
                continue

            self._logger.info("success")

    def save_fm_file(self) -> None:
        self._fm_file.update()

    def rollback_fm_file(self) -> None:
        self._fm_file = self._fm_file_class(self._fm_file_path)


class TuflowModelConverter1D(ModelConverter):
    def __init__(
        self,
        ecf_path: Union[str, Path],
        ief_path: Union[str, Path],
        log_path: Union[str, Path],
    ) -> None:

        super().__init__(IEF, ief_path, log_path)

        self._logger.info("reading files...")

        self._ecf = TuflowParser(ecf_path)
        self._logger.info("ecf done")


class TuflowModelConverter2D(ModelConverter):
    def __init__(
        self,
        tcf_path: Union[str, Path],
        xml_path: Union[str, Path],
        log_path: Union[str, Path],
    ) -> None:

        super().__init__(XML2D, xml_path, log_path)

        self._logger.info("reading files...")

        self._tcf = TuflowParser(tcf_path)
        self._logger.info("tcf done")

        for k, v in {
            "tgc": "Geometry Control File",
            "tbc": "BC Control File",
            "ecf": "ESTRY Control File",
        }.items():
            path = self._tcf.get_path(v)
            setattr(self, f"_{k}", TuflowParser(path))
            self._logger.info(f"{k} done")

        self._cc_dict = {
            "computational area": self._create_computational_area_cc,
            "topography": self._create_topography_cc,
            "roughness": self._create_roughness_cc,
            "scheme": self._create_scheme_cc,
            "boundary": self._create_boundary_cc,
        }

    def _create_computational_area_cc(self):

        return LocLineConverter(
            xml=self._fm_file,
            folder=self._processed_inputs_folder,
            domain_name="Domain 1",
            dx=self._tgc.get_value("Cell Size", float),
            lx_ly=self._tgc.get_tuple("Grid Size (X,Y)", ",", int),
            all_areas=self._tgc.get_all_geodataframes("Read GIS Code"),
            loc_line=self._tgc.get_single_geometry("Read GIS Location"),
        )

    def _create_topography_cc(self):

        return TopographyConverter(
            xml=self._fm_file,
            folder=self._processed_inputs_folder,
            domain_name="Domain 1",
            rasters=self._tgc.get_all_paths("Read GRID Zpts"),
            vectors=self._tgc.get_all_geodataframes("Read GIS Z Shape"),
        )

    def _create_roughness_cc(self):

        return RoughnessConverter(
            xml=self._fm_file,
            folder=self._processed_inputs_folder,
            domain_name="Domain 1",
            law="manning",
            global_material=self._tgc.get_value("Set Mat", int),
            file_material=self._tgc.get_all_geodataframes("Read GIS Mat"),
            mapping=self._tcf.get_dataframe("Read Materials File"),
        )

    def _create_scheme_cc(self):

        return SchemeConverter(
            xml=self._fm_file,
            folder=self._processed_inputs_folder,
            domain_name="Domain 1",
            time_step=self._tcf.get_value("Timestep", float),
            start_offset=self._tcf.get_value("Start Time", float),
            total=self._tcf.get_value("End Time", float),
            scheme=self._tcf.get_value("Solution Scheme"),
            hardware=self._tcf.get_value("Hardware"),
        )

    def _create_boundary_cc(self):

        return BoundaryConverter(
            xml=self._fm_file,
            folder=self._processed_inputs_folder,
            domain_name="Domain 1",
            vectors=self._tbc.get_all_geodataframes("Read GIS BC"),
        )
