from floodmodeller_api import IEF, XML2D
from toolbox.model_conversion.tuflow_to_floodmodeller.model_converter import (
    FMFileWrapper,
    TuflowModelConverter2D,
)

from pathlib import Path
import pytest


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

    change_timestep(fm_file_wrapper, '0.1')
    assert fm_file_wrapper.fm_file != fm_file_class(filepath)

    fm_file_wrapper.update()
    assert fm_file_wrapper.fm_file == fm_file_class(filepath)

    change_timestep(fm_file_wrapper, '0.2')
    assert fm_file_wrapper.fm_file != fm_file_class(filepath)

    fm_file_wrapper.rollback()
    assert fm_file_wrapper.fm_file == fm_file_class(filepath)
