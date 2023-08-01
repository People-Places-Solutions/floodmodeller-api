from floodmodeller_api import IEF, XML2D
from toolbox.model_conversion.tuflow_to_floodmodeller.model_converter import (
    FMFileWrapper,
    TuflowModelConverter2D,
)

from pathlib import Path


def test_fm_file_wrapper(tmpdir):

    filepath = Path.joinpath(Path(tmpdir), "test.xml")
    fm_file_wrapper = FMFileWrapper(XML2D, filepath, {})
    assert fm_file_wrapper.fm_file == XML2D(filepath)

    fm_file_wrapper.fm_file.processor = {"type": "CPU"}
    assert fm_file_wrapper.fm_file != XML2D(filepath)

    fm_file_wrapper.update()
    assert fm_file_wrapper.fm_file == XML2D(filepath)

    fm_file_wrapper.fm_file.processor = {"type": "GPU"}
    assert fm_file_wrapper.fm_file != XML2D(filepath)

    fm_file_wrapper.rollback()
    assert fm_file_wrapper.fm_file == XML2D(filepath)

    # parameterise IEF and XML2D
