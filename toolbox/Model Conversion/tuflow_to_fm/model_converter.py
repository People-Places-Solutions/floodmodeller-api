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
        self._logger.info("initialising conversion process")

        self._component_converters = {}

    def convert(self):
        self._logger.info("starting conversion process")

        for k, v in self._component_converters.items():
            self._logger.info(f"converting {k}")
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

    LOC_LINE_NAMES = {
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

        self._stage_type = "computational area"
        self._init_one_component_converter(
            [self._init_loc_line_converter],
            ["loc_line"],
            [self.LOC_LINE_NAMES],
            [self._tgc],
        )

    def _init_one_component_converter(
        self,
        cc_inits: list[callable],
        cc_names: list[str],
        cc_dicts: list[dict],
        cc_parsers: list[TuflowParser],
    ):
        self._logger.info(f"initialising {self._stage_type}")

        for cc_init, cc_name, cc_dict, cc_parser in zip(
            cc_inits, cc_names, cc_dicts, cc_parsers
        ):
            self._logger.info(f"checking for {cc_name} settings")

            if not cc_parser.check_names(cc_dict.values()):
                self._logger.info(f"{cc_name} settings not detected")
                continue

            self._logger.info(f"{cc_name} settings detected")

            try:
                cc_init(cc_dict, cc_parser)
            except:
                # self._logger.error("{cc_name} settings not valid")
                # self._logger.debug("", exc_info=True)
                self._logger.exception(f"{cc_name} settings not valid")
                continue

            self._logger.info(f"{cc_name} settings valid")
            break

    def _init_loc_line_converter(self, cc_dict: dict, cc_parser: TuflowParser):

        xml = self._xml
        inputs_folder = self._inputs_folder
        domain_name = "Domain 1"
        loc_line = cc_parser.get_single_geometry(cc_dict["loc_line"])
        dx = cc_parser.get_value(cc_dict["dx"], float)
        nx, ny = cc_parser.get_tuple(cc_dict["nx, ny"], ",", int)

        all_areas = cc_parser.get_all_geodataframes(
            cc_dict["all_areas"], case_insensitive=True
        )
        active_area = all_areas[all_areas["code"] == 1].drop(columns="code")
        deactive_area = all_areas[all_areas["code"] == 0].drop(columns="code")

        self._component_converters[self._stage_type] = LocLineConverter(
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
