import ctypes as ct
from pathlib import Path

from ._base import FMFile
from .util import get_zzn_reader, handle_exception


class ZZX(FMFile):
    _filetype: str = "ZZX"
    _suffix: str = ".zzx"

    @handle_exception(when="read")
    def __init__(self, zzn_filepath: str | Path | None = None) -> None:
        FMFile.__init__(self, zzn_filepath)
        zzn_read = get_zzn_reader()

