from pathlib import Path
from typing import Union

class TuflowParser:

    COMMENT_SYMBOL = "!"
    ASSIGNMENT_SYMBOL = "=="
    LIST_SYMBOL = "|"

    def __init__(self, file: Union[str, Path]) -> None:

        self._folder = Path(file).parents[0]

        self._contents_dict = {}

        with open(file) as f:

            for line in f:

                line = line.partition(self.COMMENT_SYMBOL)[0]

                if line.isspace() or not line:
                    continue

                k, v = line.split(self.ASSIGNMENT_SYMBOL)

                k = k.strip()
                v = v.strip()
                # v = [x.strip() for x in v.split(self.LIST_SYMBOL)]

                self._contents_dict[k] = v

    def get_raw_value(self, k: str) -> str:
        return self._contents_dict[k]

    def get_full_path(self, k: str) -> Path:
        return Path.joinpath(self._folder, self._contents_dict[k]).resolve()
