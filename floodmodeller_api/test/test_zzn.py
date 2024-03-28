from pathlib import Path

import pandas as pd
import pytest

from floodmodeller_api import ZZN


@pytest.fixture
def zzn_fp(test_workspace):
    return Path(test_workspace, "network.zzn")


@pytest.fixture
def tab_csv_output(test_workspace):
    tab_csv_output = pd.read_csv(Path(test_workspace, "network_from_tabularCSV.csv"))
    tab_csv_output["Max State"] = tab_csv_output["Max State"].astype("float64")
    return tab_csv_output


def test_load_zzn_using_dll(zzn_fp, tab_csv_output, test_workspace):
    """ZZN: Check loading zzn okay using dll"""
    zzn = ZZN(zzn_fp)
    zzn.export_to_csv(
        result_type="max",
        save_location=Path(test_workspace, "test_output.csv"),
    )
    output = pd.read_csv(Path(test_workspace, "test_output.csv"))
    output = round(output, 3)  # Round to 3dp
    # https://stackoverflow.com/questions/20274987/how-to-use-pytest-to-check-that-error-is-not-raised
    try:
        pd.testing.assert_frame_equal(output, tab_csv_output, rtol=0.0001)
    except Exception:
        pytest.fail("data frames not equal")
