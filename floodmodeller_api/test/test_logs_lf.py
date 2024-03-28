from pathlib import Path

import pandas as pd
import pytest

from floodmodeller_api import IEF, LF1


@pytest.fixture
def lf1_fp(test_workspace):
    return Path(test_workspace, "ex3.lf1")


def test_lf1_info_dict(lf1_fp):
    """LF1: Check info dictionary"""
    lf1 = LF1(lf1_fp)
    assert lf1.info["version"] == "5.0.0.7752"
    assert lf1.info["max_system_volume"] == 270549
    assert lf1.info["mass_balance_error"] == -0.03
    assert lf1.info["progress"] == 100


def test_lf1_report_progress(lf1_fp):
    """LF1: Check report_progress()"""
    lf1 = LF1(lf1_fp)
    assert lf1.report_progress() == 100


def test_lf1_to_dataframe(lf1_fp):
    """LF1: Check to_dataframe()"""
    lf1 = LF1(lf1_fp)
    df = lf1.to_dataframe()
    assert df.iloc[0, 3] == 6
    assert df.iloc[-1, -1] == 21.06
    assert df.iloc[4, 0] == -0.07


def test_lf1_from_ief(lf1_fp, test_workspace):
    """LF1: Check IEF.get_lf1()"""
    lf1 = LF1(lf1_fp)

    ief_fp = Path(test_workspace, "ex3.ief")
    ief = IEF(ief_fp)
    lf1_from_ief = ief.get_log()

    assert lf1._filepath == lf1_from_ief._filepath
    assert lf1.info == lf1_from_ief.info
    try:
        pd.testing.assert_frame_equal(lf1.to_dataframe(), lf1_from_ief.to_dataframe())
    except Exception:
        pytest.fail("Dataframes not equal")
