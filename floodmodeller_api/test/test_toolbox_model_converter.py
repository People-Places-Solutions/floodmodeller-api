from floodmodeller_api import IEF, XML2D
from toolbox.model_conversion.tuflow_to_floodmodeller.model_converter import (
    FMFileWrapper,
    TuflowModelConverter2D,
)

from pathlib import Path
import pytest

path_to_mc = "toolbox.model_conversion.tuflow_to_floodmodeller.model_converter"


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


@pytest.fixture
def tcf(tmpdir) -> str:

    tcf_name = "test_tcf.tcf"
    tgc_name = "test_tgc.tgc"
    tbc_name = "test_tbc.tbc"
    ecf_name = "test_ecf.ecf"

    tcf_contents = f"""
        geometry control file == {tgc_name}
        bc control file == {tbc_name}
        estry control file == {ecf_name}
        """
    tgc_contents = ""
    tbc_contents = ""
    ecf_contents = ""

    for name, contents in zip(
        [tcf_name, tgc_name, tbc_name, ecf_name],
        [tcf_contents, tgc_contents, tbc_contents, ecf_contents],
    ):
        with open(Path.joinpath(Path(tmpdir), name), "w") as file:
            file.write(contents)

    return tcf_name


def test_model_converter(tmpdir, tcf):

    model_name = "test_name"

    tuflow_converter = TuflowModelConverter2D(
        Path.joinpath(Path(tmpdir), tcf), tmpdir, model_name
    )

    log_path = Path.joinpath(Path(tmpdir), model_name, f"{model_name}_conversion.log")

    expected_log = [
        "reading TUFLOW files...",
        "tcf done",
        "tgc done",
        "tbc done",
        "initialising FM files...",
        "xml done",
        "reading TUFLOW files...",
        "ecf done",
        "initialising FM files...",
        "ief done",
    ]

    with open(log_path, "r") as file:
        for l1, l2 in zip(expected_log, file):
            assert f"INFO - {l1}\n" == l2.split(' - ', 1)[1]

    # tuflow_converter._xml
    # tuflow_converter._ief
    # tuflow_converter.convert_model()
    # tuflow_converter._create_computational_area_cc_2d()

    # parameterise loc line
    # parameterise estry
