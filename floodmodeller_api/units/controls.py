from __future__ import annotations

from typing import TYPE_CHECKING

from floodmodeller_api.validation import _validate_unit

from ._base import Unit
from ._helpers import (
    join_10_char,
    join_12_char_ljust,
    read_reservoir_data,
    split_10_char,
    split_12_char,
    to_float,
    to_int,
    write_dataframe,
)

if TYPE_CHECKING:
    import pandas as pd


class RESERVOIR(Unit):
    """Class to hold and process RESERVOIR unit type

    Args:
        name (str, optional): Unit name.
        comment (str, optional): Comment included in unit.
        labels (str, optional): Unlimited number of labels - not including first label (name).
        easting (float, optional): Easting coordinate of reservoir reference point (not used in computations).
        northing (float, optional): Northing coordinate of reservoir reference point (not used in computations).
        runoff_factor (float, optional): Rainfall runoff factor.
        lateral_inflow_labels (list[str], optional): Lateral inflow labels (up to 4).
        data (pandas.DataFrame): Dataframe object containing all the reservoir section data.
            Columns are ``'Elevation','Plan Area'``

    Returns:
        RESERVOIR: Flood Modeller RESERVOIR Unit class object"""

    _unit = "RESERVOIR"

    def _read(self, block: list[str]) -> None:
        self._revision, self.comment = self._get_revision_and_comment(block[0])

        self.labels = split_12_char(block[1])
        self.name = self.labels[0]

        if self._revision == 1:
            self.lateral_inflow_labels = split_12_char(block[2])
            idx = 3

            lines = split_10_char(f"{block[-1]:<30}")
            self.easting = to_float(lines[0])
            self.northing = to_float(lines[1])
            self.runoff = to_float(lines[2])
        else:
            idx = 2

        self.no_rows = to_int(block[idx])
        start_idx = idx + 1
        end_idx = start_idx + self.no_rows
        self.data = read_reservoir_data(block[start_idx:end_idx])

    def _write(self) -> list[str]:
        _validate_unit(self)
        rev1_a = (
            [join_12_char_ljust(*self.lateral_inflow_labels).rstrip()]
            if self._revision == 1
            else []
        )
        rev1_b = (
            [join_10_char(self.easting, self.northing, self.runoff)] if self._revision == 1 else []
        )
        return [
            self._create_header(include_revision=self._revision is not None),
            join_12_char_ljust(*self.labels).rstrip(),
            *rev1_a,
            *write_dataframe(self.no_rows, self.data),
            *rev1_b,
        ]

    def _create_from_blank(  # noqa: PLR0913 (need that many)
        self,
        name: str = "new_reservoir",
        comment: str = "",
        subtype: str = "OPEN",
        labels: list[str] | None = None,
        easting: float = 0.0,
        northing: float = 0.0,
        runoff: float = 0.0,
        lateral_inflow_labels: list[str] | None = None,
        data: pd.DataFrame | None = None,
    ) -> None:
        self.easting = easting
        self.northing = northing
        self.runoff = runoff
        self.name = name
        self.comment = comment
        self._subtype = subtype
        self._revision = 1
        self.labels = labels if labels is not None else []
        self.lateral_inflow_labels = (
            lateral_inflow_labels if lateral_inflow_labels is not None else []
        )

        self.data = self._enforce_dataframe(data, ("Elevation", "Plan Area"))
        self.no_rows = len(self.data)
