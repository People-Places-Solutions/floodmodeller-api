import pytest
import os
from floodmodeller_api import IEF

@pytest.fixture
def ief_fp(test_workspace):
    ief_fp = os.path.join(test_workspace, "network.ief")
    return ief_fp


@pytest.fixture
def data_before(ief_fp): 
    with open(ief_fp, "r") as ief_file:
        data_before = ief_file.read()
    return data_before

def test_ief_open_does_not_change_data(ief_fp, data_before):
    """IEF: Test str representation equal to ief file with no changes"""
    ief = IEF(ief_fp)
    assert ief._write() == data_before
