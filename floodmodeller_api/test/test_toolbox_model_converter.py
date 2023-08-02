from floodmodeller_api import IEF, XML2D
from toolbox.model_conversion.tuflow_to_floodmodeller.model_converter import (
    FMFileWrapper,
    TuflowModelConverter2D,
)

from pathlib import Path
from shapely.geometry import Point, LineString
import geopandas as gpd
import pytest


@pytest.fixture
def tcf(tmpdir) -> Path:

    tcf_name = "test_tcf.tcf"
    tgc_name = "test_tgc.tgc"
    tbc_name = "test_tbc.tbc"
    ecf_name = "test_ecf.ecf"

    code_name = "test_code.shp"
    line_name = "test_line.shp"

    tcf_str = f"""
        geometry control file == {tgc_name}
        bc control file == {tbc_name}
        estry control file == {ecf_name}
        """
    tgc_str = f"""
        cell size == 10
        grid size (x,y) == 20,30
        read gis code == {code_name}
        read gis location == {line_name}
        """
    tbc_str = ""
    ecf_str = ""

    code_gpd = gpd.GeoDataFrame({"x": [1], "geometry": [Point(0, 0)]})
    line_gpd = gpd.GeoDataFrame({"x": [1], "geometry": [LineString([(0, 0), (1, 1)])]})

    for name, contents in zip(
        [tcf_name, tgc_name, tbc_name, ecf_name, code_name, line_name],
        [tcf_str, tgc_str, tbc_str, ecf_str, code_gpd, line_gpd],
    ):
        file_path = Path.joinpath(Path(tmpdir), name)
        if isinstance(contents, str):
            with open(file_path, "w") as file:
                file.write(contents)
        elif isinstance(contents, gpd.GeoDataFrame):
            contents.to_file(file_path)

    return Path.joinpath(Path(tmpdir), tcf_name)


@pytest.mark.parametrize(
    "fm_file_class,file_name",
    [
        (XML2D, "test.xml"),
        (IEF, "test.ief"),
    ],
)
def test_fm_file_wrapper(tmpdir, fm_file_class, file_name):
    def change_timestep(fm_file_wrapper: FMFileWrapper, timestep: float) -> None:
        fm_file = fm_file_wrapper.fm_file
        if isinstance(fm_file, XML2D):
            fm_file.domains["Domain 1"]["run_data"] = {
                "time_step": timestep,
                "scheme": "TVD",
            }
        elif isinstance(fm_file, IEF):
            fm_file.Timestep = timestep

    filepath = Path.joinpath(Path(tmpdir), file_name)
    fm_file_wrapper = FMFileWrapper(fm_file_class, filepath, {})
    assert fm_file_wrapper.fm_file == fm_file_class(filepath)

    change_timestep(fm_file_wrapper, "0.1")
    assert fm_file_wrapper.fm_file != fm_file_class(filepath)

    fm_file_wrapper.update()
    assert fm_file_wrapper.fm_file == fm_file_class(filepath)

    change_timestep(fm_file_wrapper, "0.2")
    assert fm_file_wrapper.fm_file != fm_file_class(filepath)

    fm_file_wrapper.rollback()
    assert fm_file_wrapper.fm_file == fm_file_class(filepath)


def test_model_converter(tmpdir, tcf):
    def assert_log_contains(log_path, expected):
        with open(log_path, "r") as file:
            for l1, l2 in zip(file, expected):
                assert l1.split(" - ", 1)[1] == f"{l2}\n"

    model_name = "test_name"
    domain_name = "Domain 1"
    log_path = Path.joinpath(Path(tmpdir), model_name, f"{model_name}_conversion.log")

    # initialisation
    tuflow_converter = TuflowModelConverter2D(tcf, tmpdir, model_name)

    expected_xml = XML2D()
    expected_ief = IEF()
    expected_log = [
        "INFO - reading TUFLOW files...",
        "INFO - tcf done",
        "INFO - tgc done",
        "INFO - tbc done",
        "INFO - initialising FM files...",
        "INFO - xml done",
        "INFO - reading TUFLOW files...",
        "INFO - ecf done",
        "INFO - initialising FM files...",
        "INFO - ief done",
    ]

    assert_log_contains(log_path, expected_log)
    assert tuflow_converter._xml == expected_xml
    assert tuflow_converter._ief == expected_ief

    # conversion
    tuflow_converter.convert_model()

    expected_xml.domains[domain_name]["computational_area"] = {
        "xll": 0,
        "yll": 0,
        "dx": 10,
        "nrows": 2,
        "ncols": 3,
        "rotation": 45,
        "active_area": str(
            Path.joinpath(Path(tmpdir), model_name, "gis", "active_area.shp")
        ),
    }
    expected_log += [
        "INFO - converting computational area...",
        "INFO - success",
        "INFO - converting topography...",
        "ERROR - failure",
        "INFO - converting roughness...",
        "ERROR - failure",
        "INFO - converting scheme...",
        "ERROR - failure",
        "INFO - converting estry...",
        "ERROR - failure",
    ]

    assert_log_contains(log_path, expected_log)
    assert tuflow_converter._xml == expected_xml
    assert tuflow_converter._ief == expected_ief

    # parameterise loc line
    # parameterise estry
