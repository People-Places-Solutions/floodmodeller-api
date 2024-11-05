from pathlib import Path

import pytest

from floodmodeller_api import INP


@pytest.fixture()
def inp_fp(test_workspace):
    return Path(test_workspace, "network.inp")


@pytest.fixture()
def data_before(inp_fp):
    return INP(inp_fp)._write()


def test_inp_open_does_not_change_data(inp_fp, data_before):
    """INP: Test str representation equal to inp file with no changes"""
    inp = INP(inp_fp)
    assert inp._write() == data_before


def test_section_name_and_snow_catch_factor_changes(inp_fp, data_before):
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


def test_all_inp_files_in_folder_have_same_output(test_workspace, tmpdir):
    """INP: Check all '.inp' files in folder by reading the _write() output into a new INP instance and checking it stays the same."""
    for inpfile in Path(test_workspace).glob("*.inp"):
        inp = INP(inpfile)
        first_output = inp._write()
        new_path = Path(tmpdir) / "tmp.inp"
        inp.save(new_path)
        second_output = INP(new_path)._write()
        assert first_output == second_output
