import logging
from pathlib import Path
from typing import Callable, Dict, Type, Union

from floodmodeller_api import DAT, IEF, XML2D
from floodmodeller_api.toolbox.model_conversion.tuflow_to_floodmodeller.component_converter import (
    ComponentConverter,
)

from .component_converter import (
    BoundaryConverterXML2D,
    ComponentConverter,
    ComputationalAreaConverterXML2D,
    LocLineConverterXML2D,
    NetworkConverterDAT,
    RoughnessConverterXML2D,
    SchemeConverterIEF,
    SchemeConverterXML2D,
    TopographyConverterXML2D,
)
from .file_parser import TuflowParser


class FMFileWrapper:
    def __init__(
        self,
        fm_file_class: Type[Union[XML2D, IEF, DAT]],
        fm_filepath: Union[str, Path],
        cc_dict: Dict[str, Callable[..., ComponentConverter]],
        **kwargs,
    ) -> None:
        self._fm_file_class = fm_file_class
        self._fm_filepath = fm_filepath
        self.cc_dict = cc_dict
        self.fm_file = self._fm_file_class(**kwargs)
        self.fm_file.save(self._fm_filepath)

    def rollback(self) -> None:
        self.fm_file = self._fm_file_class(self._fm_filepath)

    def update(self) -> None:
        self.fm_file.update()


class TuflowModelConverter:
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
        self._processed_inputs_folder = Path.joinpath(self._root, "gis")
        self._processed_inputs_folder.mkdir(parents=True, exist_ok=True)

        self._create_logger()
        self._initialise_control_files()

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

    def _initialise_control_files(self) -> None:
        self._logger.info("reading TUFLOW files...")

        self._tcf = TuflowParser(self._tcf_path)
        self._logger.info("tcf done")

        self._tgc = TuflowParser(self._tcf.get_path("geometry control file"))
        self._logger.info("tgc done")

        self._tbc = TuflowParser(self._tcf.get_path("bc control file"))
        self._logger.info("tbc done")

        self._logger.info("initialising FM files...")

        self._fm_file_wrappers = {
            "xml": FMFileWrapper(
                fm_file_class=XML2D,
                fm_filepath=Path.joinpath(self._root, f"{self._name}.xml"),
                cc_dict={
                    "computational area": self._create_computational_area_cc_xml2d,
                    "topography": self._create_topography_cc_xml2d,
                    "roughness": self._create_roughness_cc_xml2d,
                    "scheme": self._create_scheme_cc_xml2d,
                    # "boundary": self._create_boundary_cc_xml2d,
                },
            )
        }
        self._logger.info("xml done")

        self._logger.info("reading TUFLOW files...")

        contains_estry = self._tcf.check_key("estry control file")
        if not contains_estry:
            self._logger.info("ecf not detected; no ief or dat required")
            return

        self._ecf = TuflowParser(self._tcf.get_path("estry control file"))
        self._logger.info("ecf done")

        self._logger.info("initialising FM files...")

        self._fm_file_wrappers["ief"] = FMFileWrapper(
            fm_file_class=IEF,
            fm_filepath=Path.joinpath(self._root, f"{self._name}.ief"),
            cc_dict={
                "estry": self._create_scheme_cc_ief,
            },
        )
        self._logger.info("ief done")

        self._fm_file_wrappers["dat"] = FMFileWrapper(
            fm_file_class=DAT,
            fm_filepath=Path.joinpath(self._root, f"{self._name}.dat"),
            cc_dict={
                "network and gxy": self._create_network_cc_dat,
            },
            with_gxy=True,
        )
        self._logger.info("dat done")

    @property
    def _xml(self) -> XML2D:
        return self._fm_file_wrappers["xml"].fm_file

    @property
    def _ief(self) -> IEF:
        return self._fm_file_wrappers["ief"].fm_file

    @property
    def _dat(self) -> DAT:
        return self._fm_file_wrappers["dat"].fm_file

    def convert_model(self) -> None:
        for fm_file_wrapper in self._fm_file_wrappers.values():
            for cc_display_name, cc_factory in fm_file_wrapper.cc_dict.items():
                self._logger.info(f"converting {cc_display_name}...")

                try:
                    cc_object = cc_factory()
                    cc_object.edit_fm_file()
                    fm_file_wrapper.update()
                    self._logger.info("success")

                except:
                    self._logger.exception("failure")
                    fm_file_wrapper.rollback()

    def _create_computational_area_cc_xml2d(self) -> ComputationalAreaConverterXML2D:
        dx = self._tgc.get_value("cell size", float)
        lx_ly = self._tgc.get_tuple("grid size (x,y)", ",", int)
        all_areas = self._tgc.get_all_geodataframes("read gis code")

        if self._tgc.check_key("read gis location"):
            return LocLineConverterXML2D(
                xml=self._xml,
                folder=self._processed_inputs_folder,
                domain_name=self.DOMAIN_NAME,
                dx=dx,
                lx_ly=lx_ly,
                all_areas=all_areas,
                loc_line=self._tgc.get_single_geometry("read gis location"),
            )

        return ComputationalAreaConverterXML2D(
            xml=self._xml,
            folder=self._processed_inputs_folder,
            domain_name=self.DOMAIN_NAME,
            dx=dx,
            lx_ly=lx_ly,
            all_areas=all_areas,
        )

    def _create_topography_cc_xml2d(self) -> TopographyConverterXML2D:
        vectors = (
            self._tgc.get_all_geodataframes("read gis z shape")
            if self._tgc.check_key("read gis z shape")
            else []
        )
        return TopographyConverterXML2D(
            xml=self._xml,
            folder=self._processed_inputs_folder,
            domain_name=self.DOMAIN_NAME,
            rasters=self._tgc.get_all_paths("read grid zpts"),
            vectors=vectors,
        )

    def _create_roughness_cc_xml2d(self) -> RoughnessConverterXML2D:
        return RoughnessConverterXML2D(
            xml=self._xml,
            folder=self._processed_inputs_folder,
            domain_name=self.DOMAIN_NAME,
            law="manning",
            global_material=self._tgc.get_value("set mat", int),
            file_material=self._tgc.get_all_geodataframes("read gis mat"),
            mapping=self._tcf.get_dataframe("read materials file"),
        )

    def _create_scheme_cc_xml2d(self) -> SchemeConverterXML2D:
        return SchemeConverterXML2D(
            xml=self._xml,
            folder=self._processed_inputs_folder,
            domain_name=self.DOMAIN_NAME,
            time_step=self._tcf.get_value("timestep", float),
            start_offset=self._tcf.get_value("start time", float),
            total=self._tcf.get_value("end time", float),
            scheme=self._tcf.get_value("solution scheme"),
            hardware=self._tcf.get_value("hardware"),
        )

    def _create_boundary_cc_xml2d(self) -> BoundaryConverterXML2D:
        return BoundaryConverterXML2D(
            xml=self._xml,
            folder=self._processed_inputs_folder,
            domain_name=self.DOMAIN_NAME,
            vectors=self._tbc.get_all_geodataframes("read gis bc"),
        )

    def _create_scheme_cc_ief(self) -> SchemeConverterIEF:
        return SchemeConverterIEF(
            ief=self._ief,
            folder=self._processed_inputs_folder,
            time_step=self._ecf.get_value("timestep", float),
        )

    def _create_network_cc_dat(self) -> NetworkConverterDAT:
        return NetworkConverterDAT(
            dat=self._dat,
            folder=self._processed_inputs_folder,
            parent_folder=str(self._ecf._folder),
            nwk_paths=self._ecf.get_all_paths("read gis network"),
            xs_paths=self._ecf.get_all_paths("read gis table links"),
        )
