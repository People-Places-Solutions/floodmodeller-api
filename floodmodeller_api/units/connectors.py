from __future__ import annotations

import pandas as pd

from ._base import Unit
from ._helpers import (
    join_12_char_ljust,
    read_lateral_data,
    read_reservoir_data,
    split_12_char,
    to_int,
    write_dataframe,
)


class JUNCTION(Unit):
    _unit = "JUNCTION"

    def _read(self, block: list[str]) -> None:
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
    _required_columns = ("Node Label", "Custom Weight Factor", "Use Weight Factor")

    def _read(self, block: list[str]) -> None:
        self.comment = self._remove_unit_name(block[0])
        self.name = block[1]
        self.weight_factor = block[2]
        self.no_units = to_int(block[3])
        self.data = read_lateral_data(block[4:])

    def _write(self) -> list[str]:
        return [
            self._create_header(),
            self.name,  # type: ignore
            self.weight_factor,
            *write_dataframe(self.no_units, self.data, n=12),
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

        self.data = (
            data
            if isinstance(data, pd.DataFrame)
            else pd.DataFrame(
                [],
                columns=self._required_columns,
            )
        )
        self.no_units = len(self.data)


class RESERVOIR(Unit):
    _unit = "RESERVOIR"
    _required_columns = ("Elevation", "Plan Area")

    def _read(self, block: list[str]) -> None:
        b = self._remove_unit_name(block[0], remove_revision=True)
        self._revision = to_int(b[0], 1) if b != "" else None
        self.comment = b[1:].strip()

        self.labels = split_12_char(block[1])
        self.name = self.labels[0]

        if self._revision == 1:
            self.lateral_inflow_labels = split_12_char(block[2])
            idx = 3
        else:
            idx = 2

        self.no_rows = to_int(block[idx])
        start_idx = idx + 1
        end_idx = start_idx + self.no_rows
        self.data = read_reservoir_data(block[start_idx:end_idx])

        print(self.data)

        # TODO: easting, northing, runoff for revision 1

    def _write(self) -> list[str]:
        lateral_inflow_labels = (
            [join_12_char_ljust(*self.lateral_inflow_labels).rstrip()]
            if self._revision == 1
            else []
        )
        return [
            self._create_header(include_revision=self._revision is not None),
            join_12_char_ljust(*self.labels).rstrip(),
            *lateral_inflow_labels,
            *write_dataframe(self.no_rows, self.data),
        ]

    def _create_from_blank(  # noqa: PLR0913 (need that many)
        self,
        name: str = "",
        comment: str = "",
        subtype: str = "OPEN",
        labels: list[str] | None = None,
        lateral_inflow_labels: list[str] | None = None,
        data: pd.DataFrame | None = None,
    ) -> None:
        self.name = name
        self.comment = comment
        self._subtype = subtype
        self._revision = 1
        self.labels = labels if labels is not None else []
        self.lateral_inflow_labels = (
            lateral_inflow_labels if lateral_inflow_labels is not None else []
        )

        self.data = (
            data
            if isinstance(data, pd.DataFrame)
            else pd.DataFrame(
                [],
                columns=self._required_columns,
            )
        )
        self.no_rows = len(self.data)