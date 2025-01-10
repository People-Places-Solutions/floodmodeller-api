from ._base import Unit
from .helpers import join_12_char_ljust, split_12_char


class JUNCTION(Unit):
    _unit = "JUNCTION"

    def _read(self, block: list[str]) -> None:
        self._raw_block = block

        self.comment = block[0].replace(self._unit, "").strip()
        self._subtype = block[1].split(" ")[0].strip()
        self.labels = split_12_char(block[2])

        self.name = self.labels[0]

    def _write(self) -> list[str]:
        return [
            self._unit,
            self.subtype,
            join_12_char_ljust(*self.labels).rstrip(),
        ]
