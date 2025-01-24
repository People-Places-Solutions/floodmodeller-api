from __future__ import annotations

import pandas as pd

from ._base import Unit
from .helpers import _to_int, join_12_char_ljust, split_12_char


class JUNCTION(Unit):
    _unit = "JUNCTION"

    def _read(self, block: list[str]) -> None:
        self._raw_block = block

        self.comment = self._remove_unit_name(block[0])
        self._subtype = self._get_first_word(block[1])
        self.labels = split_12_char(block[2])

        self.name = self.labels[0]

    def _write(self) -> list[str]:
        return [
            self._create_header(),
            self.subtype,  # type: ignore
            join_12_char_ljust(*self.labels).rstrip(),
        ]

    def _create_from_blank(
        self,
        comment: str = "",
        subtype: str = "OPEN",
        labels: list[str] | None = None,
    ) -> None:
        self.comment = comment
        self._subtype = subtype
        self.labels = labels if labels is not None else []
        self.name = self.labels[0]


class LATERAL(Unit):
    _unit = "LATERAL"
    _required_columns: tuple[str] = (
        "Node Label",
        "Custom Weight Factor",
        "Use Weight Factor",
    )

    def _read(self, block: list[str]) -> None:
        self._raw_block = block

        self.comment = self._remove_unit_name(block[0])
        self.name = block[1]
        self.weight_factor = block[2]
        self.no_units = _to_int(block[3])

    def _write(self) -> list[str]:
        return [
            self._create_header(),
            self.name,  # type: ignore
            self.weight_factor,
            str(self.no_units),
            *self._raw_block[4:],  # FIXME
        ]

    def _create_from_blank(
        self,
        name: str = "",
        comment: str = "",
        subtype: str = "OPEN",
        weight_factor: str = "REACH",
        data: pd.DataFrame | None = None,
    ) -> None:
        self.name = name
        self.comment = comment
        self._subtype = subtype
        self.weight_factor = weight_factor

        self._data = (
            data
            if isinstance(data, pd.DataFrame)
            else pd.DataFrame(
                [],
                columns=self._required_columns,
            )
        )
        self.no_units = len(self._data)


class RESERVOIR(Unit):
    _unit = "RESERVOIR"

    def _read(self, block: list[str]) -> None:
        self._raw_block = block

        b = self._remove_unit_name(block[0], remove_revision=True)
        self._revision = _to_int(b[0], 1) if b != "" else None
        self.comment = b[1:].strip()

        self.labels = split_12_char(block[1])
        self.name = self.labels[0]

        if self._revision == 1:
            self.lateral_inflow_labels = split_12_char(block[2])
            self.no_rows = _to_int(block[3])
        else:
            self.no_rows = _to_int(block[2])

    def _write(self) -> list[str]:
        lines = [
            self._create_header(include_revision=self._revision is not None),
            join_12_char_ljust(*self.labels).rstrip(),
        ]

        if self._revision == 1:
            lines += [
                join_12_char_ljust(*self.lateral_inflow_labels).rstrip(),
                f"{self.no_rows:>10}",
                *self._raw_block[4:],  # FIXME
            ]
        else:
            lines += [
                f"{self.no_rows:>10}",
                *self._raw_block[3:],  # FIXME
            ]
        return lines
