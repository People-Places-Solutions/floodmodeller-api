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

    def to_dataframe(self) -> pd.DataFrame:
        nx = self.meta["nnodes"]
        ny = self.meta["nvars"]
        nz = self.meta["savint_range"] + 1

        arr = self.data["all_results"]
        time_index = np.linspace(self.meta["output_hrs"][0], self.meta["output_hrs"][1], nz)
        vars_list = self.meta["variables"]  # difference from zzn

        col_names = [vars_list, self.meta["labels"]]
        df = pd.DataFrame(
            arr.reshape(nz, nx * ny),
            index=time_index,
            columns=pd.MultiIndex.from_product(col_names),
        )
        df.index.name = "Time (hr)"
        return df
