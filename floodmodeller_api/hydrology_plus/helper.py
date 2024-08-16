"""Helps to create the class for the hydrology plus"""

from __future__ import annotations

from pathlib import Path

from floodmodeller_api.hydrology_plus.hydrology_plus_export import HydrologyPlusExport


def load_hydrology_plus_csv_export(file: str | Path) -> HydrologyPlusExport:
    """
    Loads a CSV containing exported Hydrology+ flow data and returns a HydrologyPlusExport object.

    Args:
        file (str | Path): The path to the Hydrology+ export CSV file.

    Returns:
        HydrologyPlusExport: An object representing the data from the Hydrology+ export.
    """
    return HydrologyPlusExport(file)
