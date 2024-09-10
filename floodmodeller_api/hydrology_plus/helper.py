"""Helps to create the class for the hydrology plus"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .hydrology_plus_export import HydrologyPlusExport

if TYPE_CHECKING:
    from pathlib import Path


def load_hydrology_plus_csv_export(file: str | Path) -> HydrologyPlusExport:
    """
    Loads a CSV containing exported Hydrology+ flow data and returns a HydrologyPlusExport object.

    Args:
        file (str | Path): The path to the Hydrology+ export CSV file.

    Returns:
        HydrologyPlusExport: An object representing the data from the Hydrology+ export.
    """
    return HydrologyPlusExport(file)
