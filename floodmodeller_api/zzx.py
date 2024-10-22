from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from floodmodeller_api.zzn import get_all, process_zzn_or_zzx

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
        self.data, self.meta = process_zzn_or_zzx(self._filepath)
        self.variables = self.meta["variables"]

    def to_dataframe(self) -> pd.DataFrame:
        return get_all(self.data, self.meta, self.variables, "all", True)
