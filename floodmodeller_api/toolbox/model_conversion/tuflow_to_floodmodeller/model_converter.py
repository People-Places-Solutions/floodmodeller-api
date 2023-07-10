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

        self._tcf_path = tcf_path
        self._name = name
        self._root = Path.joinpath(Path(folder), self._name)
        self._root.mkdir(parents=True, exist_ok=True)

        self._create_logger()
        self._read_tuflow_files()
        self._init_fm_files()
        self._init_cc_dicts()

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

        self._xml = XML2D()
        self._xml_filepath = Path.joinpath(self._root, f"{self._name}.xml")
        self._xml.save(self._xml_filepath)
        self._logger.info("xml done")

        if self._contains_estry:
            self._ief = IEF()
            self._ief_filepath = Path.joinpath(self._root, f"{self._name}.ief")
            self._ief.save(self._ief_filepath)
            self._logger.info("ief done")

    def _init_cc_dicts(self) -> None:

        self._cc_2d_dict = {
            "computational area": self._create_computational_area_cc_2d,
            "topography": self._create_topography_cc_2d,
            "roughness": self._create_roughness_cc_2d,
            "scheme": self._create_scheme_cc_2d,
            "boundary": self._create_boundary_cc_2d,
        }

        if self._contains_estry:
            self._cc_1d_dict = {"estry": self._create_scheme_cc_1d}
        else:
            self._cc_1d_dict = {}

    def convert_model(self) -> None:

        # 2D
        for cc_class_display_name, cc_factory in self._cc_2d_dict.items():

            self._logger.info(f"converting {cc_class_display_name}...")

            try:
                cc_object = cc_factory()
                cc_object.edit_xml()
                self._xml.update()
                self._logger.info("success")
            except:
                self._logger.exception("failure")
                self._xml = XML2D(self._xml_filepath)  # rollback

        # 1D estry
        for cc_class_display_name, cc_factory in self._cc_1d_dict.items():

            self._logger.info(f"converting {cc_class_display_name}...")

            try:
                cc_object = cc_factory()
                cc_object.edit_ief()
                self._ief.update()
                self._logger.info("success")
            except:
                self._logger.exception("failure")
                self._ief = IEF(self._ief_filepath)  # rollback

    def _create_computational_area_cc_2d(self) -> LocLineConverter2D:

        return LocLineConverter2D(
            xml=self._xml,
            folder=self._processed_inputs_folder,
            domain_name="Domain 1",
            dx=self._tgc.get_value("cell size", float),
            lx_ly=self._tgc.get_tuple("grid size (x,y)", ",", int),
            all_areas=self._tgc.get_all_geodataframes("read gis code"),
            loc_line=self._tgc.get_single_geometry("read gis location"),
        )

    def _create_topography_cc_2d(self) -> TopographyConverter2D:

        return TopographyConverter2D(
            xml=self._xml,
            folder=self._processed_inputs_folder,
            domain_name="Domain 1",
            rasters=self._tgc.get_all_paths("read grid zpts"),
            vectors=self._tgc.get_all_geodataframes("read gis z shape"),
        )

    def _create_roughness_cc_2d(self) -> RoughnessConverter2D:

        return RoughnessConverter2D(
            xml=self._xml,
            folder=self._processed_inputs_folder,
            domain_name="Domain 1",
            law="manning",
            global_material=self._tgc.get_value("set mat", int),
            file_material=self._tgc.get_all_geodataframes("read gis mat"),
            mapping=self._tcf.get_dataframe("read materials file"),
        )

    def _create_scheme_cc_2d(self) -> SchemeConverter2D:

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

    def _create_boundary_cc_2d(self) -> BoundaryConverter2D:

        return BoundaryConverter2D(
            xml=self._xml,
            folder=self._processed_inputs_folder,
            domain_name="Domain 1",
            vectors=self._tbc.get_all_geodataframes("read gis bc"),
        )

    def _create_scheme_cc_1d(self) -> SchemeConverter1D:

        return SchemeConverter1D(
            ief=self._ief,
            folder=self._processed_inputs_folder,
            time_step=self._ecf.get_value("timestep", float),
        )
