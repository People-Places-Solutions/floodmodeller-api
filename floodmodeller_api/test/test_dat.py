import logging
from pathlib import Path
from unittest.mock import patch

import pytest

from floodmodeller_api import DAT
from floodmodeller_api.units import JUNCTION, LATERAL, QTBDY, RESERVOIR, UNSUPPORTED
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


@pytest.fixture()
def unsupported_dummy_unit():
    data = [
        "APITESTDUMMY Dummy unnsupported unit for testing purposes",
        "LBL001      LBL002",
        "arbitrary data",
        "        table01234",
        "    -0.500     0.000     0.000    0.000091000000.0",
        "     0.000     1.000     1.000    0.0000 910000000",
        "     1.000     2.000     2.000    0.000091000000.0",
        "     2.000     3.000     3.000    0.000091000000.0",
        "     5.000     3.000     3.000    0.000091000000.0",
    ]
    return UNSUPPORTED(
        data,
        12,
        unit_name="LBL001",
        unit_type="APITESTDUMMY",
        subtype=False,
    )


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


def test_dat_read_doesnt_change_data(test_workspace, tmp_path):
    """DAT: Check all '.dat' files in folder by reading the _write() output into a new DAT instance and checking it stays the same."""
    for datfile in Path(test_workspace).glob("*.dat"):
        if datfile.name.startswith("duplicate_unit_test"):
            # Skipping as invalid DAT (duplicate units)
            continue
        dat = DAT(datfile)
        first_output = dat._write()
        new_path = tmp_path / "tmp.dat"
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
        "INFO     root:_base.py:141 Files not equivalent, 12 difference(s) found:\n"
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


def test_diff_active_data(test_workspace):
    dat = DAT(Path(test_workspace, "ex4.DAT"))
    dat_copy = DAT(Path(test_workspace, "ex4.DAT"))
    assert dat == dat_copy

    for section in dat.sections.values():
        if section.unit == "RIVER":
            _ = section.active_data

    assert dat == dat_copy


def test_valid_network(test_workspace: Path):
    """Test against network derived manually."""
    dat = DAT(test_workspace / "network.dat")
    actual_nodes, actual_edges = dat.get_network()

    expected_edges = [
        ("FSSR16BDY_resin", "RIVER_resin"),
        ("QTBDY_CS26", "RIVER_CS26"),
        ("RIVER_CS26", "RIVER_CS25"),
        ("RIVER_CS25", "RIVER_CS24"),
        ("RIVER_CS25", "SPILL_RD25Su"),
        ("RIVER_CS24", "RIVER_CS23"),
        ("RIVER_CS24", "SPILL_RD24Su"),
        ("RIVER_CS23", "RIVER_CS22"),
        ("RIVER_CS23", "SPILL_RD23Su"),
        ("RIVER_CS22", "RIVER_CS21"),
        ("RIVER_CS22", "SPILL_RD22Su"),
        ("RIVER_CS21", "RIVER_CS20"),
        ("RIVER_CS21", "SPILL_RD21Su"),
        ("RIVER_CS20", "RIVER_CS19"),
        ("RIVER_CS20", "SPILL_RD20Su"),
        ("RIVER_CS19", "RIVER_CS18"),
        ("RIVER_CS19", "SPILL_RD19Su"),
        ("RIVER_CS18", "RIVER_RESOUT2a"),
        ("RIVER_CS18", "SPILL_RD18Su"),
        ("RIVER_RESOUT2a", "RIVER_RESOUT2b"),
        ("RIVER_RESOUT2b", "JUNCTION_RESOUT2b"),
        ("JUNCTION_RESOUT2b", "RIVER_RESOUT2u"),
        ("JUNCTION_RESOUT2b", "RIVER_RESOUT2d"),
        ("RIVER_resin", "RIVER_CSRD25"),
        ("RIVER_CSRD25", "RIVER_CSRD24"),
        ("RIVER_CSRD25", "SPILL_RD25Su"),
        ("RIVER_CSRD24", "RIVER_CSRD23"),
        ("RIVER_CSRD24", "SPILL_RD24Su"),
        ("RIVER_CSRD23", "RIVER_CSRD22"),
        ("RIVER_CSRD23", "SPILL_RD23Su"),
        ("RIVER_CSRD22", "RIVER_CSRD21"),
        ("RIVER_CSRD22", "SPILL_RD22Su"),
        ("RIVER_CSRD21", "RIVER_CSRD20"),
        ("RIVER_CSRD21", "SPILL_RD21Su"),
        ("RIVER_CSRD20", "RIVER_CSRD19"),
        ("RIVER_CSRD20", "SPILL_RD20Su"),
        ("RIVER_CSRD19", "RIVER_CSRD18"),
        ("RIVER_CSRD19", "SPILL_RD19Su"),
        ("RIVER_CSRD18", "RIVER_CSRD17"),
        ("RIVER_CSRD18", "SPILL_RD18Su"),
        ("RIVER_CSRD17", "RIVER_CSRD16"),
        ("RIVER_CSRD16", "RIVER_CSRD15"),
        ("RIVER_CSRD15", "RIVER_CSRD14u"),
        ("RIVER_CSRD14u", "JUNCTION_CSRD14u"),
        ("JUNCTION_CSRD14u", "RNWEIR_MILLBu"),
        ("JUNCTION_CSRD14u", "RNWEIR_MILLAu"),
        ("RNWEIR_MILLAu", "RIVER_MILLAd"),
        ("RIVER_MILLAd", "RIVER_RESOUT2u"),
        ("RIVER_RESOUT2d", "RIVER_CSRD13"),
        ("RIVER_CSRD13", "RIVER_CSRD12u"),
        ("RIVER_CSRD12u", "JUNCTION_CSRD12u"),
        ("RNWEIR_MILLBu", "JUNCTION_CSRD12u"),
        ("JUNCTION_CSRD12u", "RIVER_CSRD12d"),
        ("RIVER_CSRD12d", "RIVER_CSRD10"),
        ("RIVER_CSRD10", "RIVER_CSRD09"),
        ("RIVER_CSRD09u", "RIVER_CSRD09a"),
        ("RIVER_CSRD09", "JUNCTION_CSRD09"),
        ("RIVER_CSRD09u", "JUNCTION_CSRD09"),
        ("JUNCTION_CSRD09", "RNWEIR_ROAD1"),
        ("RIVER_CSRD09a", "BERNOULLI_CSRD09a"),
        ("BERNOULLI_CSRD09a", "RIVER_CSRD08u"),
        ("RIVER_CSRD08u", "RIVER_CSRD08a"),
        ("RIVER_CSRD08a", "JUNCTION_CSRD08a"),
        ("JUNCTION_CSRD08a", "RIVER_CSRD08"),
        ("RNWEIR_ROAD1", "JUNCTION_CSRD08a"),
        ("RIVER_CSRD08", "RIVER_CSRD07"),
        ("RIVER_CSRD07", "RIVER_CSRD06"),
        ("RIVER_CSRD06", "RIVER_CSRD05"),
        ("RIVER_CSRD05", "RIVER_CSRD04"),
        ("RIVER_CSRD04", "RIVER_CSRD03"),
        ("RIVER_CSRD03", "RIVER_CSRD02"),
        ("RIVER_CSRD02", "RIVER_CSRD02d"),
        ("RIVER_CSRD02d", "JUNCTION_CSRD02d"),
        ("JUNCTION_CSRD02d", "RNWEIR_RAILRDu"),
        ("JUNCTION_CSRD02d", "BERNOULLI_RAILBRu"),
        ("BERNOULLI_RAILBRu", "JUNCTION_RAILBRd"),
        ("RNWEIR_RAILRDu", "JUNCTION_RAILBRd"),
        ("JUNCTION_RAILBRd", "RIVER_CSRD01a"),
        ("RIVER_CSRD01a", "RIVER_CSRD01u"),
        ("RIVER_CSRD01u", "RNWEIR_CSRD01u"),
        ("RNWEIR_CSRD01u", "RIVER_CSRD01d"),
        ("RIVER_CSRD01d", "RIVER_CSRD01"),
        ("RIVER_CSRD01", "INTERPOLATE_DS.001"),
        ("INTERPOLATE_DS.001", "INTERPOLATE_DS.002"),
        ("INTERPOLATE_DS.002", "INTERPOLATE_DS.003"),
        ("INTERPOLATE_DS.003", "INTERPOLATE_DS.004"),
        ("INTERPOLATE_DS.004", "INTERPOLATE_DS.005"),
        ("INTERPOLATE_DS.005", "INTERPOLATE_DS.006"),
        ("INTERPOLATE_DS.006", "RIVER_DS2"),
        ("RIVER_DS2", "JUNCTION_DS2"),
        ("JUNCTION_DS2", "RNWEIR_FOOTa"),
        ("JUNCTION_DS2", "BERNOULLI_FOOTBRu"),
        ("RNWEIR_FOOTa", "JUNCTION_FOOTb"),
        ("BERNOULLI_FOOTBRu", "JUNCTION_FOOTb"),
        ("JUNCTION_FOOTb", "RIVER_DS3"),
        ("RIVER_DS3", "RIVER_DS4"),
        ("RIVER_DS4", "QHBDY_DS4"),
    ]

    actual = {tuple(x.unique_name for x in y) for y in actual_edges}
    expected = set(expected_edges)
    assert expected == actual
    assert len(actual_nodes) == 86


def test_invalid_network(test_workspace: Path):
    """Test dat file that cannot be made into a valid network."""
    dat = DAT(test_workspace / "All Units 4_6.DAT")
    with pytest.raises(RuntimeError):
        dat.get_network()


def test_create_and_insert_connectors():
    dat = DAT()
    junction = JUNCTION(comment="hi", labels=["A", "B"])
    lateral = LATERAL(name="lat", comment="bye")
    reservoir = RESERVOIR(
        easting=0,
        northing=0,
        runoff=0,
        name="res",
        comment="hello",
        lateral_inflow_labels=["C", "D"],
    )
    dat.insert_units([junction, lateral, reservoir], add_at=-1)
    assert dat.connectors == {"A": junction, "lat": lateral}
    assert dat.controls == {"res": reservoir}


@pytest.mark.parametrize(
    ("dat_str", "label"),
    [
        ("encoding_test_utf8.dat", "d\xc3\xa5rek"),  # because it's initially saved as utf8
        ("encoding_test_cp1252.dat", "d\xe5rek"),
    ],
)
def test_encoding(test_workspace: Path, dat_str: str, label: str, tmp_path: Path):
    dat_read = DAT(test_workspace / dat_str)
    new_path = tmp_path / "tmp_encoding.dat"
    dat_read.save(new_path)
    dat_write = DAT(new_path)

    assert label in dat_read.sections
    assert label in dat_write.sections  # remains as \xc3\xa5 even for utf8


def test_insert_unsupported_unit(tmp_path: Path, unsupported_dummy_unit):
    new_dat = DAT()
    new_dat.insert_unit(unsupported_dummy_unit, add_at=-1)
    assert unsupported_dummy_unit in new_dat._unsupported.values()
    assert len(new_dat._all_units) == 1
    filepath = tmp_path / "insert_dummy_test.dat"
    new_dat.save(filepath)

    dat = DAT(filepath)
    assert unsupported_dummy_unit in dat._unsupported.values()
    assert len(dat._all_units) == 1


def test_remove_unsupported_unit(test_workspace, unsupported_dummy_unit):
    dat = DAT(test_workspace / "remove_dummy_test.dat")
    assert len(dat._all_units) == 1
    assert len(dat._dat_struct) == 3
    assert len(dat.initial_conditions.data) == 1
    assert "LBL001 (APITESTDUMMY)" in dat._unsupported
    dat.remove_unit(unsupported_dummy_unit)
    assert len(dat._all_units) == 0
    assert len(dat._dat_struct) == 2
    assert len(dat.initial_conditions.data) == 0
    assert "LBL001 (APITESTDUMMY)" not in dat._unsupported
    dat._write()
    assert len(dat._all_units) == 0
    assert len(dat._dat_struct) == 2
    assert len(dat.initial_conditions.data) == 0
    assert "LBL001 (APITESTDUMMY)" not in dat._unsupported


def test_duplicate_unit_raises_error(test_workspace):
    msg = (
        r"\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        r"\nAPI Error: Problem encountered when trying to read DAT file .*\."
        r"\n"
        r"\nDetails: .*-floodmodeller_api/dat\.py-\d+"
        r"\nMsg: Duplicate label (.*) encountered within category: .*"
        r"\n"
        r"\nFor additional support, go to: https://github\.com/People-Places-Solutions/floodmodeller-api"
    )
    with pytest.raises(FloodModellerAPIError, match=msg):
        DAT(test_workspace / "duplicate_unit_test.dat")
    with pytest.raises(FloodModellerAPIError, match=msg):
        DAT(test_workspace / "duplicate_unit_test_unsupported.dat")
