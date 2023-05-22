from floodmodeller_api import IEF, XML2D
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


class TuflowModelConverter2D:
    def __init__(
        self,
        tcf_path: Union[str, Path],
        folder: Union[str, Path],
        name: str,
    ) -> None:

        self._root = Path.joinpath(Path(folder), name)
        self._root.mkdir(parents=True, exist_ok=True)

        self._logger = self._create_logger(Path.joinpath(self._root, f"{name}.log"))

        self._read_tuflow_files(tcf_path)
        self._init_fm_files(name)

        self._cc_dict = {
            "computational area": self._create_computational_area_cc,
            "topography": self._create_topography_cc,
            "roughness": self._create_roughness_cc,
            "scheme": self._create_scheme_cc,
            "boundary": self._create_boundary_cc,
        }

        if self._contains_estry:
            self._cc_dict["estry"] = self._create_estry_cc

    def _create_logger(self, log_name: Path) -> logging.Logger:

        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        logging.basicConfig(
            filename=log_name,
            filemode="w",
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%H:%M:%S",
            level=logging.INFO,
        )
        return logging.getLogger(__name__)

    def _read_tuflow_files(self, tcf_path: Union[str, Path]):

        self._logger.info("reading TUFLOW files...")

        self._tcf = TuflowParser(tcf_path)
        self._logger.info("tcf done")

        self._tgc = TuflowParser(self._tcf.get_path("geometry control file"))
        self._logger.info("tgc done")

        self._tbc = TuflowParser(self._tcf.get_path("bc control file"))
        self._logger.info("tbc done")

        self._contains_estry = self._tcf.check_key("estry control file")

        if self._contains_estry:
            self._ecf = TuflowParser(self._tcf.get_path("estry control file"))
            self._logger.info("ecf done")
        else:
            self._logger.info("ecf not detected")

    def _init_fm_files(self, name: str):

        self._logger.info("initialising Flood Modeller files...")

        self._processed_inputs_folder = Path.joinpath(self._root, "gis")
        self._processed_inputs_folder.mkdir(parents=True, exist_ok=True)

        self._xml = XML2D()
        self._xml_filepath = Path.joinpath(self._root, f"{name}.xml")
        self._xml.save(self._xml_filepath)
        self._logger.info("xml done")

        if self._contains_estry:
            self._ief = IEF()
            self._ief_filepath = Path.joinpath(self._root, f"{name}.ief")
            self._ief.save(self._ief_filepath)
            self._logger.info("ief done")

    def convert_model(self) -> None:

        for cc_class_display_name, cc_factory in self._cc_dict.items():

            self._logger.info(f"converting {cc_class_display_name}...")

            try:
                cc_object = cc_factory()
                cc_object.edit_fm_file()
                self.save_fm_file()
                self._logger.info("success")
            except:
                self._logger.exception("failure")
                self.rollback_fm_file()

    def save_fm_file(self) -> None:
        self._xml.update()
        if self._contains_estry:
            self._ief.update()

    def rollback_fm_file(self) -> None:
        self._xml = XML2D(self._xml_filepath)
        if self._contains_estry:
            self._ief = IEF(self._ief_filepath)

    def _create_computational_area_cc(self):

        return LocLineConverter2D(
            xml=self._xml,
            folder=self._processed_inputs_folder,
            domain_name="Domain 1",
            dx=self._tgc.get_value("cell size", float),
            lx_ly=self._tgc.get_tuple("grid size (x,y)", ",", int),
            all_areas=self._tgc.get_all_geodataframes("read gis code"),
            loc_line=self._tgc.get_single_geometry("read gis location"),
        )

    def _create_topography_cc(self):

        return TopographyConverter2D(
            xml=self._xml,
            folder=self._processed_inputs_folder,
            domain_name="Domain 1",
            rasters=self._tgc.get_all_paths("read grid zpts"),
            vectors=self._tgc.get_all_geodataframes("read gis z shape"),
        )

    def _create_roughness_cc(self):

        return RoughnessConverter2D(
            xml=self._xml,
            folder=self._processed_inputs_folder,
            domain_name="Domain 1",
            law="manning",
            global_material=self._tgc.get_value("set mat", int),
            file_material=self._tgc.get_all_geodataframes("read gis mat"),
            mapping=self._tcf.get_dataframe("read materials file"),
        )

    def _create_scheme_cc(self):

        return SchemeConverter2D(
            xml=self._xml,
            folder=self._processed_inputs_folder,
            domain_name="Domain 1",
            time_step=self._tcf.get_value("timestep", float),
            start_offset=self._tcf.get_value("start time", float),
            total=self._tcf.get_value("end time", float),
            scheme=self._tcf.get_value("solution scheme"),
            hardware=self._tcf.get_value("hardware"),
        )

    def _create_boundary_cc(self):

        return BoundaryConverter2D(
            xml=self._xml,
            folder=self._processed_inputs_folder,
            domain_name="Domain 1",
            vectors=self._tbc.get_all_geodataframes("read gis bc"),
        )

    def _create_estry_cc(self):

        return SchemeConverter1D(
            ief=self._ief,
            folder=self._processed_inputs_folder,
            time_step=self._ecf.get_value("timestep", float),
        )
