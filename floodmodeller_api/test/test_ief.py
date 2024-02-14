import os

import pytest

from floodmodeller_api import IEF


@pytest.fixture
def ief_fp(test_workspace):
    return os.path.join(test_workspace, "network.ief")


@pytest.fixture
def data_before(ief_fp):
    with open(ief_fp) as ief_file:
        return ief_file.read()


def test_ief_open_does_not_change_data(ief_fp, data_before):
    """IEF: Test str representation equal to ief file with no changes"""
    ief = IEF(ief_fp)
    assert ief._write() == data_before
