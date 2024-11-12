import pytest

from floodmodeller_api import read_file
from floodmodeller_api.util import FloodModellerAPIError


def test_read_file(test_workspace):
    for file in test_workspace.glob("*"):
        if (
            file.suffix.lower()
            in [
                ".ief",
                ".dat",
                ".ied",
                ".xml",
                ".zzn",
                ".zzx",
                ".inp",
                ".lf1",
                ".lf2",
            ]
            or file.name in ["example_h+_export.csv", "Baseline_unchecked.csv"]
            or file.name.startswith("hplus_export_example")
        ):
            read_file(file)
        else:
            with pytest.raises((ValueError, FloodModellerAPIError)):
                read_file(file)
