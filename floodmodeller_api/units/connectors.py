from __future__ import annotations

from typing import TYPE_CHECKING

from floodmodeller_api.validation import _validate_unit

from ._base import Unit
from ._helpers import (
    join_12_char_ljust,
    read_lateral_data,
    split_12_char,
    to_int,
    write_dataframe,
)

if TYPE_CHECKING:
    import pandas as pd


class JUNCTION(Unit):
    """Class to hold and process JUNCTION unit type

    Args:
        comment (str, optional): Comment included in unit.
        subtype (str, optional): Defines the type of junction unit (*Should not be changed*)
        labels (str, optional): Unlimited number of labels, the first of which is the name.

    Returns:
        JUNCTION: Flood Modeller JUNCTION Unit class object"""

    _unit = "JUNCTION"

    def _read(self, block: list[str]) -> None:
        self.comment = self._remove_unit_name(block[0])
        self._subtype = self._get_first_word(block[1])
        self.labels = split_12_char(block[2])

        self.name = self.labels[0]

    def _write(self) -> list[str]:
        _validate_unit(self)
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
    """Class to hold and process LATERAL unit type

    Args:
        name (str, optional): Unit name.
        comment (str, optional): Comment included in unit.
        subtype (str, optional): Defines the type of lateral unit (*Should not be changed*)
        weight_factor (str, optional): Corresponding weight factors or user-defined area for
            each receiving unit
        data (pandas.DataFrame): Dataframe object containing all the reservoir section data.
            Columns are ``'Node Label', 'Custom Weight Factor', 'Use Weight Factor'``

    Returns:
        LATERAL: Flood Modeller LATERAL Unit class object"""

    _unit = "LATERAL"

    def _read(self, block: list[str]) -> None:
        self.comment = self._remove_unit_name(block[0])
        self.name = block[1]
        self.weight_factor = block[2]
        self.no_units = to_int(block[3])
        self.data = read_lateral_data(block[4:])
        self.labels = list(self.data["Node Label"])

    def _write(self) -> list[str]:
        _validate_unit(self)
        return [
            self._create_header(),
            self.name,  # type: ignore
            self.weight_factor,
            *write_dataframe(self.no_units, self.data, n=12),
        ]

    def _create_from_blank(
        self,
        name: str = "new_junction",
        comment: str = "",
        subtype: str = "OPEN",
        weight_factor: str = "REACH",
        data: pd.DataFrame | None = None,
    ) -> None:
        self.name = name
        self.comment = comment
        self._subtype = subtype
        self.weight_factor = weight_factor

        self.data = self._enforce_dataframe(
            data,
            ("Node Label", "Custom Weight Factor", "Use Weight Factor"),
        )
        self.no_units = len(self.data)
        self.labels = list(self.data["Node Label"])
