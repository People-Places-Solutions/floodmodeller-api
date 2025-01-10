from ._base import Unit
from .helpers import _to_int, join_12_char_ljust, split_12_char


class JUNCTION(Unit):
    _unit = "JUNCTION"

    def _read(self, block: list[str]) -> None:
        self._raw_block = block

        self.comment = self._remove_unit_name(block[0])
        self._subtype = block[1].split(" ")[0].strip()
        self.labels = split_12_char(block[2])

        self.name = self.labels[0]

    def _write(self) -> list[str]:
        return [
            self._unit,
            self.subtype,
            join_12_char_ljust(*self.labels).rstrip(),
        ]


class LATERAL(Unit):
    _unit = "LATERAL"

    def _read(self, block: list[str]) -> None:
        self._raw_block = block

        self.comment = self._remove_unit_name(block[0])
        self.name = block[1]
        self.weight_factor = block[2]
        self.no_units = _to_int(block[3])

    def _write(self) -> list[str]:
        return [
            f"{self._unit} {self.comment}",
            self.name,
            self.weight_factor,
            str(self.no_units),
            *self._raw_block[4:],
        ]
