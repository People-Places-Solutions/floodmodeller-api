from pathlib import Path

import pandas as pd
import pytest

from floodmodeller_api import IEF, ZZN


@pytest.fixture
def zzn(test_workspace: Path) -> ZZN:
    path = test_workspace / "network.zzn"
    return ZZN(path)


@pytest.fixture
def ief(test_workspace: Path) -> IEF:
    path = test_workspace / "network.ief"
    return IEF(path)


@pytest.fixture
def tab_csv_output(test_workspace: Path) -> pd.DataFrame:
    tab_csv_output = pd.read_csv(test_workspace / "network_from_tabularCSV.csv")
    tab_csv_output["Max State"] = tab_csv_output["Max State"].astype("float64")
    return tab_csv_output


def test_load_zzn_using_dll(zzn: ZZN, tab_csv_output: pd.DataFrame, tmp_path: Path):
    """ZZN: Check loading zzn okay using dll"""
    test_output_path = tmp_path / "test_output.csv"
    zzn.export_to_csv(result_type="max", save_location=test_output_path)
    output = pd.read_csv(test_output_path).round(3)
    pd.testing.assert_frame_equal(output, tab_csv_output, rtol=0.0001)


def _test_load_zzn_using_dll():
    pass


def test_load_zzn_using_ief(zzn: ZZN, ief: IEF):
    zzn_df = zzn.to_dataframe()
    zzn_from_ief = ief.get_results().to_dataframe()
    pd.testing.assert_frame_equal(zzn_df, zzn_from_ief)
