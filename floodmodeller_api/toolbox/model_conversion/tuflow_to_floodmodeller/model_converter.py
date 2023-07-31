from floodmodeller_api import IEF, XML2D
from .file_parser import TuflowParser
from .component_converter import (
    ComponentConverter,
    SchemeConverter1D,
    ComputationalAreaConverter2D,
    LocLineConverter2D,
    TopographyConverter2D,
    RoughnessConverter2D,
    SchemeConverter2D,
    BoundaryConverter2D,
)

from pathlib import Path
from typing import Union, Dict, Callable, Type
import logging


class FMFileWrapper:
    def __init__(
        self,
        cc_dict: Dict[str, Callable[..., ComponentConverter]],
        fm_file_class: Type[Union[XML2D, IEF]],
        fm_filepath: Union[str, Path],
    ) -> None:
        self.cc_dict = cc_dict
        self.fm_file_class = fm_file_class
        self.fm_filepath = fm_filepath
        self.fm_file = self.fm_file_class()
        self.fm_file.save(self.fm_filepath)

    def rollback(self) -> None:
        self.fm_file = self.fm_file_class(self.fm_filepath)

    def update(self) -> None:
        self.fm_file.update()


class TuflowModelConverter2D:

    DOMAIN_NAME = "Domain 1"

    def __init__(
        self,
        tcf_path: Union[str, Path],
        folder: Union[str, Path],
        name: str,
    ) -> None:

        self._tcf_path = tcf_path
        self._name = name
        self._root = Path.joinpath(Path(folder), self._name)
        self._root.mkdir(parents=True, exist_ok=True)

        self._create_logger()
        self._read_tuflow_files()
        self._init_fm_files()

    def _create_logger(self) -> None:

        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        logging.basicConfig(
            filename=Path.joinpath(self._root, f"{self._name}_conversion.log"),
            filemode="w",
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%H:%M:%S",
            level=logging.INFO,
        )
        self._logger = logging.getLogger(__name__)

    def _read_tuflow_files(self) -> None:

        self._logger.info("reading TUFLOW files...")

        self._tcf = TuflowParser(self._tcf_path)
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

    def _init_fm_files(self) -> None:

        self._logger.info("initialising Flood Modeller files...")

        self._processed_inputs_folder = Path.joinpath(self._root, "gis")
        self._processed_inputs_folder.mkdir(parents=True, exist_ok=True)

        self._fm_files = {
            "xml": FMFileWrapper(
                cc_dict={
                    "computational area": self._create_computational_area_cc_2d,
                    "topography": self._create_topography_cc_2d,
                    "roughness": self._create_roughness_cc_2d,
                    "scheme": self._create_scheme_cc_2d,
                    "boundary": self._create_boundary_cc_2d,
                },
                fm_file_class=XML2D,
                fm_filepath=Path.joinpath(self._root, f"{self._name}.xml"),
            )
        }
        self._logger.info("xml done")

        if self._contains_estry:
            self._fm_files["ief"] = FMFileWrapper(
                cc_dict={"estry": self._create_scheme_cc_1d},
                fm_file_class=IEF,
                fm_filepath=Path.joinpath(self._root, f"{self._name}.ief"),
            )
            self._logger.info("ief done")

    @property
    def _xml(self):
        return self._fm_files["xml"].fm_file
    
    @property
    def _ief(self):
        return self._fm_files["ief"].fm_file

    def convert_model(self) -> None:

        for fm_file_config in self._fm_files.values():

            for cc_class_display_name, cc_factory in fm_file_config.cc_dict.items():

                self._logger.info(f"converting {cc_class_display_name}...")

                try:
                    cc_object = cc_factory()
                    cc_object.edit_fm_file()
                    fm_file_config.update()
                    self._logger.info("success")

                except:
                    self._logger.exception("failure")
                    fm_file_config.rollback()

    def _create_computational_area_cc_2d(self) -> ComputationalAreaConverter2D:

        dx = self._tgc.get_value("cell size", float)
        lx_ly = self._tgc.get_tuple("grid size (x,y)", ",", int)
        all_areas = self._tgc.get_all_geodataframes("read gis code")

        if self._tgc.check_key("read gis location"):
            return LocLineConverter2D(
                xml=self._xml,
                folder=self._processed_inputs_folder,
                domain_name=self.DOMAIN_NAME,
                dx=dx,
                lx_ly=lx_ly,
                all_areas=all_areas,
                loc_line=self._tgc.get_single_geometry("read gis location"),
            )

        return ComputationalAreaConverter2D(
            xml=self._xml,
            folder=self._processed_inputs_folder,
            domain_name=self.DOMAIN_NAME,
            dx=dx,
            lx_ly=lx_ly,
            all_areas=all_areas,
        )

    def _create_topography_cc_2d(self) -> TopographyConverter2D:

        return TopographyConverter2D(
            xml=self._xml,
            folder=self._processed_inputs_folder,
            domain_name=self.DOMAIN_NAME,
            rasters=self._tgc.get_all_paths("read grid zpts"),
            vectors=self._tgc.get_all_geodataframes("read gis z shape"),
        )

    def _create_roughness_cc_2d(self) -> RoughnessConverter2D:

        return RoughnessConverter2D(
            xml=self._xml,
            folder=self._processed_inputs_folder,
            domain_name=self.DOMAIN_NAME,
            law="manning",
            global_material=self._tgc.get_value("set mat", int),
            file_material=self._tgc.get_all_geodataframes("read gis mat"),
            mapping=self._tcf.get_dataframe("read materials file"),
        )

    def _create_scheme_cc_2d(self) -> SchemeConverter2D:

        return SchemeConverter2D(
            xml=self._xml,
            folder=self._processed_inputs_folder,
            domain_name=self.DOMAIN_NAME,
            time_step=self._tcf.get_value("timestep", float),
            start_offset=self._tcf.get_value("start time", float),
            total=self._tcf.get_value("end time", float),
            scheme=self._tcf.get_value("solution scheme"),
            hardware=self._tcf.get_value("hardware"),
        )

    def _create_boundary_cc_2d(self) -> BoundaryConverter2D:

        return BoundaryConverter2D(
            xml=self._xml,
            folder=self._processed_inputs_folder,
            domain_name=self.DOMAIN_NAME,
            vectors=self._tbc.get_all_geodataframes("read gis bc"),
        )

    def _create_scheme_cc_1d(self) -> SchemeConverter1D:

        return SchemeConverter1D(
            ief=self._ief,
            folder=self._processed_inputs_folder,
            time_step=self._ecf.get_value("timestep", float),
        )
