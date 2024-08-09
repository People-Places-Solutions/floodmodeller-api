"""Helps to create the class for the hydrology plus"""

from pathlib import Path

from floodmodeller_api.hydrology_plus.hydrology_plus_export import HydrologyPlusExport


def load_hydrology_plus_csv_export(file: Path):

    return HydrologyPlusExport(file)
