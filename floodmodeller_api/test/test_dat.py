import logging
from pathlib import Path
from unittest.mock import patch

import pytest

from floodmodeller_api import DAT
from floodmodeller_api.units import QTBDY
from floodmodeller_api.util import FloodModellerAPIError


@pytest.fixture()
def dat_fp(test_workspace):
    return Path(test_workspace, "network.dat")


@pytest.fixture()
def data_before(dat_fp):
    return DAT(dat_fp)._write()


@pytest.fixture()
def dat_ex3(test_workspace):
    return DAT(Path(test_workspace, "EX3.DAT"))


@pytest.fixture()
def units(dat_ex3):
    unit_1 = dat_ex3.sections["20"]
    unit_2 = dat_ex3.sections["40"]
    unit_3 = dat_ex3.sections["60"]
    return [unit_1, unit_2, unit_3]


@pytest.fixture()
def dat_ex6(test_workspace):
    dat = DAT(Path(test_workspace, "EX6.DAT"))
    with (
        patch.object(dat, "_update_raw_data", wraps=dat._update_raw_data),
        patch.object(dat, "_update_dat_struct", wraps=dat._update_dat_struct),
    ):
        yield dat


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
        if isinstance(unit, QTBDY):
            prev_qt[name] = unit.data.copy()
            unit.data *= 2  # Multiply QT flow data by 2
    assert dat._write() != data_before

    for name, qt in prev_qt.items():
        dat.boundaries[name].data = qt  # replace QT flow data with original
    assert dat._write() == data_before


def test_dat_read_doesnt_change_data(test_workspace, tmpdir):
    """DAT: Check all '.dat' files in folder by reading the _write() output into a new DAT instance and checking it stays the same."""
    for datfile in Path(test_workspace).glob("*.dat"):
        dat = DAT(datfile)
        first_output = dat._write()
        new_path = Path(tmpdir) / "tmp.dat"
        dat.save(new_path)
        second_dat = DAT(new_path)
        assert dat == second_dat, f"dat objects not equal for {datfile=}"
        second_output = second_dat._write()
        assert first_output == second_output, f"dat outputs not equal for {datfile=}"


def test_insert_unit_before(units, dat_ex6):
    dat_ex6.insert_unit(units[0], add_before=dat_ex6.sections["P4000"])
    assert "20" in dat_ex6.sections
    assert dat_ex6._all_units[8:10] == [units[0], dat_ex6.sections["P4000"]]
    dat_ex6._update_raw_data.assert_called_once()
    dat_ex6._update_dat_struct.assert_called_once()


def test_insert_unit_after(units, dat_ex6):
    dat_ex6.insert_unit(units[0], add_after=dat_ex6.sections["P4000"])
    assert "20" in dat_ex6.sections
    assert dat_ex6._all_units[8:10] == [dat_ex6.sections["P4000"], units[0]]
    dat_ex6._update_raw_data.assert_called_once()
    dat_ex6._update_dat_struct.assert_called_once()


def test_insert_unit_at(units, dat_ex6):
    dat_ex6.insert_unit(units[0], add_at=2)
    assert "20" in dat_ex6.sections
    assert dat_ex6._all_units[2] == units[0]
    dat_ex6._update_raw_data.assert_called_once()
    dat_ex6._update_dat_struct.assert_called_once()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"add_at": 1, "add_before": 2},
        {"add_at": 1, "add_after": 3},
        {"add_before": 2, "add_after": 3},
        {"add_at": 1, "add_before": 2, "add_after": 3},
    ],
)
def test_insert_unit_too_many_arguments_error(dat_ex6, units, kwargs):
    msg = (
        r"\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        r"\nAPI Error: Problem encountered when trying to insert unit into DAT file .*\."
        r"\n"
        r"\nDetails: .*-floodmodeller_api/dat\.py-\d+"
        r"\nMsg: Only one of add_at, add_before, or add_after required"
        r"\n"
        r"\nFor additional support, go to: https://github\.com/People-Places-Solutions/floodmodeller-api"
    )
    with pytest.raises(FloodModellerAPIError, match=msg):
        dat_ex6.insert_unit(units[0], **kwargs)


def test_insert_unit_no_arguments_error(dat_ex6, units):
    msg = (
        r"\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        r"\nAPI Error: Problem encountered when trying to insert unit into DAT file .*\."
        r"\n"
        r"\nDetails: .*-floodmodeller_api/dat\.py-\d+"
        r"\nMsg: No positional argument given\. Please provide either add_before, add_at or add_after"
        r"\n"
        r"\nFor additional support, go to: https://github\.com/People-Places-Solutions/floodmodeller-api"
    )
    with pytest.raises(FloodModellerAPIError, match=msg):
        dat_ex6.insert_unit(units[0])


def test_insert_units_before(units, dat_ex6):
    dat_ex6.insert_units(units, add_before=dat_ex6.sections["P4000"])
    assert "20" in dat_ex6.sections
    assert "40" in dat_ex6.sections
    assert "60" in dat_ex6.sections
    assert dat_ex6._all_units[8:12] == [*units, dat_ex6.sections["P4000"]]
    dat_ex6._update_raw_data.assert_called_once()
    dat_ex6._update_dat_struct.assert_called_once()


def test_insert_units_after(units, dat_ex6):
    dat_ex6.insert_units(units, add_after=dat_ex6.sections["P4000"])
    assert "20" in dat_ex6.sections
    assert "40" in dat_ex6.sections
    assert "60" in dat_ex6.sections
    assert dat_ex6._all_units[8:12] == [dat_ex6.sections["P4000"], *units]
    dat_ex6._update_raw_data.assert_called_once()
    dat_ex6._update_dat_struct.assert_called_once()


def test_insert_units_at(units, dat_ex6):
    dat_ex6.insert_units(units, add_at=2)
    assert "20" in dat_ex6.sections
    assert "40" in dat_ex6.sections
    assert "60" in dat_ex6.sections
    assert dat_ex6._all_units[2:5] == units
    dat_ex6._update_raw_data.assert_called_once()
    dat_ex6._update_dat_struct.assert_called_once()


def test_insert_units_at_end(units, dat_ex6):
    dat_ex6.insert_units(units, add_at=-1)
    assert "20" in dat_ex6.sections
    assert "40" in dat_ex6.sections
    assert "60" in dat_ex6.sections
    assert dat_ex6._all_units[-3:] == units
    dat_ex6._update_raw_data.assert_called_once()
    dat_ex6._update_dat_struct.assert_called_once()


def test_remove_unit(dat_ex3):
    unit = dat_ex3.sections["20"]
    prev_dat_struct_len = len(dat_ex3._dat_struct)
    dat_ex3.remove_unit(unit)
    assert "20" not in dat_ex3.sections
    assert unit not in dat_ex3._all_units
    assert dat_ex3._dat_struct
    assert (prev_dat_struct_len - len(dat_ex3._dat_struct)) == 1


def test_diff(test_workspace, caplog):
    with caplog.at_level(logging.INFO):
        dat_ex4 = DAT(Path(test_workspace, "ex4.DAT"))
        dat_ex4_changed = DAT(Path(test_workspace, "ex4_changed.DAT"))
        dat_ex4.diff(dat_ex4_changed)

    assert caplog.text == (
        "INFO     root:_base.py:134 Files not equivalent, 12 difference(s) found:\n"
        "  DAT->structures->MILLAu->RNWEIR..MILLAu->upstream_crest_height:  1.07 != 1.37\n"
        "  DAT->structures->MILLBu->RNWEIR..MILLBu->upstream_crest_height:  0.43 != 0.73\n"
        "  DAT->structures->ROAD1->RNWEIR..ROAD1->upstream_crest_height:  2.02 != 2.32\n"
        "  DAT->structures->RAILRDu->RNWEIR..RAILRDu->upstream_crest_height:  1.75 != 2.05\n"
        "  DAT->structures->CSRD01u->RNWEIR..CSRD01u->upstream_crest_height:  0.81 != 1.11\n"
        "  DAT->structures->FOOTa->RNWEIR..FOOTa->upstream_crest_height:  2.47 != 2.77\n"
        "  DAT->_all_units->itm[28]->RNWEIR..MILLAu->upstream_crest_height:  1.07 != 1.37\n"
        "  DAT->_all_units->itm[29]->RNWEIR..MILLBu->upstream_crest_height:  0.43 != 0.73\n"
        "  DAT->_all_units->itm[42]->RNWEIR..ROAD1->upstream_crest_height:  2.02 != 2.32\n"
        "  DAT->_all_units->itm[57]->RNWEIR..RAILRDu->upstream_crest_height:  1.75 != 2.05\n"
        "  DAT->_all_units->itm[61]->RNWEIR..CSRD01u->upstream_crest_height:  0.81 != 1.11\n"
        "  DAT->_all_units->itm[73]->RNWEIR..FOOTa->upstream_crest_height:  2.47 != 2.77\n"
    )
