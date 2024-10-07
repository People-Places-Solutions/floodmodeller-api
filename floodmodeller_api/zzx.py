from pathlib import Path

from floodmodeller_api.zzn import run_routines

from ._base import FMFile
from .util import handle_exception


class ZZX(FMFile):
    _filetype: str = "ZZX"
    _suffix: str = ".zzx"

    @handle_exception(when="read")
    def __init__(self, zzn_filepath: str | Path | None = None) -> None:
        FMFile.__init__(self, zzn_filepath)
        self.data, self.meta = run_routines(self._filepath, is_quality=False)
