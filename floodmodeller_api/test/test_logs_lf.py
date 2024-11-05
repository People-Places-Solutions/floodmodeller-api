from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from freezegun import freeze_time

from floodmodeller_api import IEF, LF1
from floodmodeller_api.logs import create_lf


@pytest.fixture()
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
    lf1_df = lf1.to_dataframe()
    assert lf1_df.loc[lf1_df.index[0], "iter"] == 6
    assert lf1_df.loc[lf1_df.index[-1], "outflow"] == 21.06
    assert lf1_df.loc[lf1_df.index[4], "mass_error"] == -0.07


def test_lf1_from_ief(lf1_fp, test_workspace):
    """LF1: Check IEF.get_lf1()"""
    lf1 = LF1(lf1_fp)

    ief_fp = Path(test_workspace, "ex3.ief")
    ief = IEF(ief_fp)
    lf1_from_ief = ief.get_log()

    assert lf1.filepath == lf1_from_ief.filepath
    assert lf1.info == lf1_from_ief.info
    pd.testing.assert_frame_equal(lf1.to_dataframe(), lf1_from_ief.to_dataframe())


def test_log_file_unsupported(capsys):
    lf = create_lf(None, "lf3")

    assert lf is None
    assert (
        capsys.readouterr().out
        == "No progress bar as log file must have suffix lf1 or lf2. Simulation will continue as usual.\n"
    )


@pytest.mark.usefixtures("log_timeout")
def test_log_file_timeout(capsys):
    lf_filepath = MagicMock()
    lf_filepath.is_file.return_value = False
    lf = create_lf(lf_filepath, "lf1")

    assert lf is None
    assert (
        capsys.readouterr().out
        == "No progress bar as log file is expected but not detected. Simulation will continue as usual.\n"
    )


@pytest.mark.usefixtures("log_timeout")
@freeze_time("1970-01-01 00:00:00", tick=True)
def test_log_file_from_old_run(capsys):
    lf_filepath = MagicMock()
    lf_filepath.is_file.return_value = True
    lf_filepath.stat.return_value.st_mtime = -10
    lf = create_lf(lf_filepath, "lf1")

    assert lf is None
    assert (
        capsys.readouterr().out
        == "No progress bar as log file is from previous run. Simulation will continue as usual.\n"
    )


@pytest.mark.usefixtures("log_timeout")
@freeze_time("1970-01-01 00:00:00", tick=True)
def test_log_file_found():
    lf_filepath = MagicMock()
    lf_filepath.is_file.return_value = True
    lf_filepath.stat.return_value.st_mtime = -1
    with patch("floodmodeller_api.logs.lf.LF1") as lf1:
        lf = create_lf(lf_filepath, "lf1")

    assert lf is not None
    lf1.assert_called_once_with(lf_filepath)
