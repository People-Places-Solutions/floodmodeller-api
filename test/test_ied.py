import os
import pytest
from floodmodeller_api import IED

@pytest.fixture
def test_workspace():
    return os.path.join(os.path.dirname(__file__), "test_data")

@pytest.fixture
def ied_fp(test_workspace):
    return os.path.join(test_workspace, "network.ied")

def test_1(ied_fp):
    """IED: Test str representation equal to ied file with no changes"""
    with open(ied_fp, "r") as ied_file:
        data_before = ied_file.read()
    ied = IED(ied_fp)
    assert ied._write() == data_before