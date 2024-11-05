from pathlib import Path

import pytest

from floodmodeller_api import IED


@pytest.fixture()
def ied_fp(test_workspace):
    return Path(test_workspace, "network.ied")


@pytest.fixture()
def ied_fp_comments(test_workspace):
    return Path(test_workspace, "network_with_comments.ied")


def test_open_ied_does_not_change_file(ied_fp):
    """IED: Test str representation equal to ied file with no changes"""
    with open(ied_fp) as ied_file:
        data_before = ied_file.read()
    ied = IED(ied_fp)
    assert ied._write() == data_before
    ied = IED(ied_fp)
    cs26_expected = [
        "QTBDY ",
        "CS26",
        "         4     0.000     0.000   seconds  NOEXTEND    LINEAR     0.000     0.000  OVERRIDE",
        "     1.000     0.000",
        "     1.000 46800.000",
        "     0.000 47160.000",
        "     0.000 1.000e+09",
    ]
    assert ied.boundaries["CS26"]._write() == cs26_expected


def test_ied_with_comments(ied_fp_comments):
    with open(ied_fp_comments) as ied_file:
        data_before = ied_file.read()
    ied = IED(ied_fp_comments)
    assert ied._write() == data_before
