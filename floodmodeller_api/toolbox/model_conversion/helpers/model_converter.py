from floodmodeller_api import IEF, XML2D
from floodmodeller_api._base import FMFile
from .file_parser import TuflowParser
from .component_converter import (
    SchemeConverter1D,
    LocLineConverter2D,
    TopographyConverter2D,
    RoughnessConverter2D,
    SchemeConverter2D,
    BoundaryConverter2D,
)

from pathlib import Path
from typing import Union
import logging


class ModelConverter:

    _cc_dict: dict
    _mc_dict: dict

    PROCESSED_INPUTS_FOLDER_NAME = "gis"

    def __init__(
        self,
        fm_file_class: FMFile,
        fm_file_path: Union[str, Path],
        log_path: Union[str, Path] = None,
        logger: logging.Logger = None,
    ) -> None:

        self._fm_file_class = fm_file_class
        self._fm_file_path = fm_file_path

        self._logger = self._create_logger(log_path, logger)

        self._fm_file = self._fm_file_class()
        self._fm_file.save(self._fm_file_path)

        self._processed_inputs_folder = Path.joinpath(
            Path(self._fm_file_path).parents[0], self.PROCESSED_INPUTS_FOLDER_NAME
        )
        self._processed_inputs_folder.mkdir(parents=True, exist_ok=True)

    def _create_logger(
        self, log_path: Union[str, Path], logger: logging.Logger
    ) -> logging.Logger:

        if (log_path and logger) or (not log_path and not logger):
            raise RuntimeError("Exactly one of log_path and logger is required")

        if logger:
            return logger

        logging.basicConfig(
            filename=log_path,
            filemode="w",
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%H:%M:%S",
            level=logging.INFO,
        )
        return logging.getLogger("model_converter")

    def convert_model(self) -> None:

        # component converter
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

        # model converter (recursive)
        for mc_class_display_name, mc_factory in self._mc_dict.items():

            self._logger.info(f"converting {mc_class_display_name}...")

            try:
                mc_object = mc_factory()
                mc_object.convert_model()
            except:
                self._logger.exception("failure")
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

        self._cc_dict = {"scheme": self._create_scheme_cc}
        self._mc_dict = {}

    def _create_scheme_cc(self):

        return SchemeConverter1D(
            ief=self._fm_file,
            folder=self._processed_inputs_folder,
            time_step=self._ecf.get_value("Timestep", float),
        )


class TuflowModelConverter2D(ModelConverter):
    def __init__(
        self,
        tcf_path: Union[str, Path],
        xml_path: Union[str, Path],
        log_path: Union[str, Path],
        ief_path: Union[str, Path] = None,
    ) -> None:

        super().__init__(XML2D, xml_path, log_path)

        self._ief_path = ief_path

        self._logger.info("reading files...")

        self._tcf = TuflowParser(tcf_path)
        self._logger.info("tcf done")

        self._tgc = TuflowParser(self._tcf.get_path("Geometry Control File"))
        self._logger.info("tgc done")

        self._tbc = TuflowParser(self._tcf.get_path("BC Control File"))
        self._logger.info("tbc done")

        self._cc_dict = {
            "computational area": self._create_computational_area_cc,
            "topography": self._create_topography_cc,
            "roughness": self._create_roughness_cc,
            "scheme": self._create_scheme_cc,
            "boundary": self._create_boundary_cc,
        }

        self._mc_dict = {
            "estry": self._convert_estry,
        }

    def _create_computational_area_cc(self):

        return LocLineConverter2D(
            xml=self._fm_file,
            folder=self._processed_inputs_folder,
            domain_name="Domain 1",
            dx=self._tgc.get_value("Cell Size", float),
            lx_ly=self._tgc.get_tuple("Grid Size (X,Y)", ",", int),
            all_areas=self._tgc.get_all_geodataframes("Read GIS Code"),
            loc_line=self._tgc.get_single_geometry("Read GIS Location"),
        )

    def _create_topography_cc(self):

        return TopographyConverter2D(
            xml=self._fm_file,
            folder=self._processed_inputs_folder,
            domain_name="Domain 1",
            rasters=self._tgc.get_all_paths("Read GRID Zpts"),
            vectors=self._tgc.get_all_geodataframes("Read GIS Z Shape"),
        )

    def _create_roughness_cc(self):

        return RoughnessConverter2D(
            xml=self._fm_file,
            folder=self._processed_inputs_folder,
            domain_name="Domain 1",
            law="manning",
            global_material=self._tgc.get_value("Set Mat", int),
            file_material=self._tgc.get_all_geodataframes("Read GIS Mat"),
            mapping=self._tcf.get_dataframe("Read Materials File"),
        )

    def _create_scheme_cc(self):

        return SchemeConverter2D(
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

        return BoundaryConverter2D(
            xml=self._fm_file,
            folder=self._processed_inputs_folder,
            domain_name="Domain 1",
            vectors=self._tbc.get_all_geodataframes("Read GIS BC"),
        )

    def _convert_estry(self):

        return TuflowModelConverter1D(
            ecf_path=self._tcf.get_path("ESTRY Control File"),
            ief_path=self._ief_path,
            log_path=self._logger,
        )
