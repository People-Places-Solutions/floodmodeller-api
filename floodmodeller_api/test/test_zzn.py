from pathlib import Path

import pandas as pd
import pytest

from floodmodeller_api import IEF, ZZN


@pytest.fixture
def zzn_fp(test_workspace):
    return Path(test_workspace, "network.zzn")


@pytest.fixture
def tab_csv_output(test_workspace):
    tab_csv_output = pd.read_csv(Path(test_workspace, "network_from_tabularCSV.csv"))
    tab_csv_output["Max State"] = tab_csv_output["Max State"].astype("float64")
    return tab_csv_output


def test_load_zzn_using_dll(zzn_fp, tab_csv_output, tmpdir):
    """ZZN: Check loading zzn okay using dll"""
    zzn = ZZN(zzn_fp)
    zzn.export_to_csv(
        result_type="max",
        save_location=Path(tmpdir, "test_output.csv"),
    )
    output = pd.read_csv(Path(tmpdir, "test_output.csv"))
    output = round(output, 3)
    pd.testing.assert_frame_equal(output, tab_csv_output, rtol=0.0001)


def test_load_zzn_using_ief(zzn_fp):
    zzn = ZZN(zzn_fp).to_dataframe()
    zzn_from_ief = IEF(zzn_fp.with_suffix(".ief")).get_results().to_dataframe()
    pd.testing.assert_frame_equal(zzn, zzn_from_ief)
