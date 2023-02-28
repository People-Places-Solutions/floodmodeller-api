from floodmodeller_api import DAT 
from floodmodeller_api.units import QTBDY

from pathlib import Path
import os
import pytest 

@pytest.fixture
def test_workspace():
    return os.path.join(os.path.dirname(__file__), "test_data")

@pytest.fixture
def dat_fp(test_workspace):
    return os.path.join(test_workspace, "network.DAT")

@pytest.fixture
def data_before(dat_fp):
    return DAT(dat_fp)._write()




def test_1(dat_fp, data_before):
    """DAT: Test str representation equal to dat file with no changes"""
    dat = DAT(dat_fp)
    assert dat._write() == data_before

def test_2(dat_fp, data_before):
    """DAT: Test changing and reverting section name and dist to next makes no changes"""
    dat = DAT(dat_fp)
    prev_name = dat.sections["CSRD10"].name
    prev_dist = dat.sections["CSRD10"].dist_to_next
    dat.sections["CSRD10"].name = "check"
    dat.sections["CSRD10"].dist_to_next = 0.0
    assert dat._write() != data_before

    dat.sections["check"].name = prev_name
    dat.sections["check"].dist_to_next = prev_dist
    assert dat._write() == data_before

def test_3(dat_fp, data_before):
    """DAT: Test changing and reverting QTBDY hydrograph makes no changes"""
    dat = DAT(dat_fp)
    prev_qt = {}
    for name, unit in dat.boundaries.items():
        if type(unit) == QTBDY:
            prev_qt[name] = unit.data.copy()
            unit.data *= 2  # Multiply QT flow data by 2
    assert dat._write() != data_before

    for name, qt in prev_qt.items():
        dat.boundaries[name].data = qt  # replace QT flow data with original
    assert dat._write() ==  data_before

def test_4(dat_fp, data_before, test_workspace):
    """DAT: Check all '.dat' files in folder by reading the _write() output into a new DAT instance and checking it stays the same."""
    for datfile in Path(test_workspace).glob("*.dat"):
        dat = DAT(datfile)
        first_output = dat._write()
        dat.save("__temp.dat")
        second_output = DAT("__temp.dat")._write()
        assert first_output == second_output
        os.remove("__temp.dat")
    try:
        os.remove("__temp.gxy")
    except FileNotFoundError:
        pass