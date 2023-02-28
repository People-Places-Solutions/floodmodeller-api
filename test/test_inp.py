from floodmodeller_api import INP 
from pathlib import Path
import os
import pytest 

@pytest.fixture
def test_workspace():
    return os.path.join(os.path.dirname(__file__), "test_data")

@pytest.fixture
def inp_fp(test_workspace):
    return  os.path.join(test_workspace, "network.inp")

@pytest.fixture
def data_before(inp_fp):
    return INP(inp_fp)._write()


def test_1(inp_fp, data_before):
    """INP: Test str representation equal to inp file with no changes"""
    inp = INP(inp_fp)
    assert inp._write() == data_before

def test_2(inp_fp, data_before):
    """INP: Test changing and reverting section name and snow catch factor makes no changes"""
    inp = INP(inp_fp)
    prev_name = inp.raingauges["1"].name
    prev_scf = inp.raingauges["1"].snow_catch_factor
    inp.raingauges["1"].name = "check"
    inp.raingauges["1"].snow_catch_factor = 1.5
    assert inp._write() != data_before

    inp.raingauges["check"].name = prev_name
    inp.raingauges["check"].snow_catch_factor = prev_scf

    assert inp._write() == data_before

def test_4(test_workspace):
    """INP: Check all '.inp' files in folder by reading the _write() output into a new INP instance and checking it stays the same."""
    for inpfile in Path(test_workspace).glob("*.inp"):
        inp = INP(inpfile)
        first_output = inp._write()
        inp.save("__temp.inp")
        second_output = INP("__temp.inp")._write()
        assert first_output == second_output
        os.remove("__temp.inp")