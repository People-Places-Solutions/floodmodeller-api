from __future__ import annotations

from typing import TYPE_CHECKING

from floodmodeller_api.zzn import convert_data, convert_meta, run_routines

from ._base import FMFile
from .util import handle_exception

if TYPE_CHECKING:
    from pathlib import Path


class ZZX(FMFile):
    _filetype: str = "ZZX"
    _suffix: str = ".zzx"

    @handle_exception(when="read")
    def __init__(self, zzx_filepath: str | Path | None = None) -> None:
        FMFile.__init__(self, zzx_filepath)
        self.data, self.meta = run_routines(self._filepath, is_quality=True)
        convert_data(self.data)
        convert_meta(self.meta)
