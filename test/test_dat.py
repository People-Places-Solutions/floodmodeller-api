from floodmodeller_api import DAT 
from floodmodeller_api.units import QTBDY

from pathlib import Path
import os
import pytest 

@pytest.fixture
def dat_fp(test_workspace):
    return os.path.join(test_workspace, "network.DAT")

@pytest.fixture
def data_before(dat_fp):
    return DAT(dat_fp)._write()




def test_dat_str_not_changed_by_write(dat_fp, data_before):
    # TODO: Update this test - it isn't really testing anything since the behaviour of the fixture is exactly the same
    """DAT: Test str representation equal to dat file with no changes"""
    dat = DAT(dat_fp)
    assert dat._write() == data_before

def test_changing_section_and_dist_works(dat_fp, data_before):
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

def test_changing_and_reverting_qtbdy_hydrograph_works(dat_fp, data_before):
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

def test_dat_read_doesnt_change_data(test_workspace):
    """DAT: Check all '.dat' files in folder by reading the _write() output into a new DAT instance and checking it stays the same."""
    for datfile in Path(test_workspace).glob("*.dat"):
        dat = DAT(datfile)
        first_output = dat._write()
        dat.save("__temp.dat")
        second_dat = DAT("__temp.dat")
        assert dat == second_dat # Checks equivalence on the class itself
        second_output = second_dat._write()
        assert first_output == second_output
        os.remove("__temp.dat")
    try:
        os.remove("__temp.gxy")
    except FileNotFoundError:
        pass