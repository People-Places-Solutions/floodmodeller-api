import copy
import csv
import subprocess
from pathlib import Path

import pandas as pd
import pytest

from floodmodeller_api import DAT
from floodmodeller_api.toolbox import StructureLog
from floodmodeller_api.toolbox.model_build.structure_log import StructureLogBuilder
from floodmodeller_api.units.conduits import CONDUIT
from floodmodeller_api.units.structures import ORIFICE


@pytest.fixture
def slb():
    return StructureLogBuilder("", "")


@pytest.fixture
def conduit_empty():
    c = CONDUIT()
    c.dist_to_next = 0
    c.friction_above_axis = 0
    c.friction_below_axis = 0
    c.height_crown = 0
    c.height_springing = 0
    c.height = 0
    c.width = 0
    c.diameter = 0
    c.friction_on_invert = 0
    c.friction_on_soffit = 0
    c.friction_on_walls = 0
    c.coords = pd.DataFrame(
        data={
            "x": [0, 0],
            "y": [0, 0],
            "cw_friction": [0, 0],
        },
    )
    return c


@pytest.fixture
def conduit_filled():
    c = CONDUIT()
    c.dist_to_next = 0
    c.friction_above_axis = 1.453345
    c.friction_below_axis = 3.435
    c.height_crown = 23.1
    c.height_springing = 5.4
    c.height = 25.45
    c.width = 3
    c.diameter = 6
    c.friction_on_invert = 1.876
    c.friction_on_soffit = 1.34
    c.friction_on_walls = 1.8
    c.coords = pd.DataFrame(
        data={
            "x": [34, 43, 45, 3, 12, 7, 78],
            "y": [0, 0, 4, 5, 10, 65, 32],
            "cw_friction": [0, 0, 0, 3, 4, 3.5, 2],
        },
    )
    return c


@pytest.fixture
def no_length():
    return 0


@pytest.fixture
def with_length():
    return 4.973


@pytest.fixture
def structure():
    return ORIFICE()


@pytest.fixture
def conduit_chain_dat(conduit_filled):
    dat = DAT()
    names = ["first", "second", "third", "fourth"]
    for name in names:
        cond = copy.deepcopy(conduit_filled)
        cond.dist_to_next = 10
        cond.name = name
        dat.conduits[name] = cond
        dat._all_units.append(cond)

    cond = copy.deepcopy(conduit_filled)
    cond.dist_to_next = 0
    cond.name = "fifth"
    dat.conduits["fifth"] = cond
    dat._all_units.append(cond)
    return dat


@pytest.fixture
def ex18_dat_path():
    return "floodmodeller_api/test/test_data/EX18.DAT"


@pytest.fixture
def ex18_dat_expected():
    # I think this is the correct way to establish the same 'expected' result, but if this is a larger/more structure-rich dat, could read from file?
    # Ideally I'd use a larger dat for this like one of the ones from private sample-dataset, to be discussed
    return """Unit Name,Unit Type,Unit Subtype,Comment,Friction,Dimensions (m),Weir Coefficient,Culvert Inlet/Outlet Loss
C2,CONDUIT,CIRCULAR,,"Mannings: [min: 0.015, max: 0.020]",dia: 1.00 x l: 100.00 (Total conduit length: 500.00),,Ki: 0.6
C2_R1,REPLICATE,,,,,,
C2_R2,REPLICATE,,,,,,
C2_R3,REPLICATE,,,,,,
C2_R4,REPLICATE,,,,,,
C2m,CONDUIT,CIRCULAR,,"Mannings: [min: 0.015, max: 0.020]",dia: 1.00 x l: 0.00,,
C2md,CONDUIT,CIRCULAR,,"Mannings: [min: 0.015, max: 0.020]",dia: 1.00 x l: 100.00 (Total conduit length: 700.00),,
C2_R5,REPLICATE,,,,,,
C2_R6,REPLICATE,,,,,,
C2_R7,REPLICATE,,,,,,
C2_R8,REPLICATE,,,,,,
C2_R9,REPLICATE,,,,,,
C2_R10,REPLICATE,,,,,,
C2d,CONDUIT,CIRCULAR,,"Mannings: [min: 0.015, max: 0.020]",dia: 1.00 x l: 0.00,,
S0,WEIR,,,,Crest Elevation: 21.00 x w: 1.50,,
C2d,WEIR,,,,Crest Elevation: 18.00 x w: 0.60,,
S4,WEIR,,,,Crest Elevation: 17.90 x w: 2.00,,
S8,WEIR,,,,Crest Elevation: 17.70 x w: 2.00,,
S3LS,SPILL,,,,Elevation: 20.00 x w: 100.00,1.7,
"""


def test_conduit_data(slb, conduit_empty):
    slb._dat = DAT()
    output = slb._conduit_data(conduit_empty)
    assert output == {
        "length": 0.0,
        "inlet": "",
        "outlet": "",
        "total_length": 0.0,
    }  # currently this expects the inlet and outlet values to be empty strings, because we're not returning lists this could probably be left out now


def test_culvert_loss_data(slb):
    output = slb._culvert_loss_data("", "")
    assert output == ""
    output = slb._culvert_loss_data("TEST1", "TEST2")
    assert output == "Ki: TEST1, Ko: TEST2"


def test_circular_data(slb, conduit_empty, conduit_filled, no_length, with_length):
    slb._dat = DAT()
    output = slb._circular_data(conduit_empty, no_length)
    assert output == ["Mannings: 0", "dia: 0.00 x l: 0.00"]
    output = slb._circular_data(conduit_filled, with_length)
    assert output == [
        "Mannings: [min: 1.453345, max: 3.435]",
        "dia: 6.00 x l: 4.97",
    ]


def test_sprungarch_data(slb, conduit_empty, conduit_filled, no_length, with_length):
    output = slb._sprungarch_data(conduit_empty, no_length)
    assert output == [
        "Mannings: 0",
        "(Springing: 0.00, Crown: 0.00) x w: 0.00 x l: 0.00",
    ]
    output = slb._sprungarch_data(conduit_filled, with_length)
    assert output == [
        "Mannings: [min: 1.34, max: 1.876]",
        "(Springing: 23.10, Crown: 5.40) x w: 3.00 x l: 4.97",
    ]


def test_rectangular_data(slb, conduit_empty, conduit_filled, no_length, with_length):
    output = slb._rectangular_data(conduit_empty, no_length)
    assert output == ["Mannings: 0", "h: 0.00 x w: 0.00 x l: 0.00"]
    output = slb._rectangular_data(conduit_filled, with_length)
    assert output == [
        "Mannings: [min: 1.34, max: 1.876]",
        "h: 25.45 x w: 3.00 x l: 4.97",
    ]


def test_section_data(slb, conduit_empty, conduit_filled, no_length, with_length):
    output = slb._section_data(conduit_empty, no_length)
    assert output == ["Colebrook-White: 0", "h: 0.00 x w: 0.00 x l: 0.00"]
    output = slb._section_data(conduit_filled, with_length)
    assert output == [
        "Colebrook-White: [min: 0.0, max: 4.0]",
        "h: 65.00 x w: 150.00 x l: 4.97",
    ]


def test_sprung_data(slb, conduit_empty, conduit_filled, no_length, with_length):
    output = slb._sprung_data(conduit_empty, no_length)
    assert output == [
        "Mannings: 0",
        "(Springing: 0.00, Crown: 0.00) x w: 0.00 x l: 0.00",
    ]
    output = slb._sprung_data(conduit_filled, with_length)
    assert output == [
        "Mannings: [min: 1.34, max: 1.876]",
        "(Springing: 23.10, Crown: 5.40) x w: 3.00 x l: 4.97",
    ]


def test_orifice_dimensions(slb, structure):
    structure.invert = 1
    output = slb._orifice_dimensions(structure)
    assert output == "h: -1.00 x w: -1.00"


def test_spill_data(slb, structure):
    structure.data = pd.DataFrame(data={"X": [0, 0], "Y": [0, 0]})
    structure.weir_coefficient = 0
    output = slb._spill_data(structure)
    assert output == ["Elevation: 0.00 x w: 0.00", 0]


def test_bridge_data(slb, structure):
    structure.section_data = pd.DataFrame(data={"X": [0, 0], "Y": [0, 0], "Mannings n": [0, 0]})
    structure.opening_data = pd.DataFrame(
        data={"Start": 0, "Finish": 0, "Springing Level": 0, "Soffit Level": 0},
        index=[0],
    )
    output = slb._bridge_data(structure)
    assert output == ["Mannings: 0", "h: 0.00 x w: 0.00"]


def test_add_conduits(slb, conduit_filled, tmpdir):
    # this test doesnt assert anything, and Im not sure what its trying to test.
    slb._dat = DAT()
    prev_c = copy.deepcopy(conduit_filled)
    prev_c.dist_to_next = 0
    prev_c.name = "prev"
    slb._dat.conduits["prev"] = prev_c
    conduit_filled.dist_to_next = 5
    slb._dat.conduits["test_conduit"] = conduit_filled
    next_c = copy.deepcopy(conduit_filled)
    next_c.dist_to_next = 0
    slb._dat.conduits["next"] = next_c
    slb._dat._all_units = [prev_c, conduit_filled, next_c]
    conduit_non_subtype = copy.deepcopy(conduit_filled)
    conduit_non_subtype._subtype = "NON_SUBTYPE"
    slb._dat.conduits["test_conduit_NON_SUBTYPE"] = conduit_non_subtype

    tmp_csv = Path(tmpdir) / "temp_structure_data.csv"
    with tmp_csv.open("w") as file:
        slb._writer = csv.writer(file)
        slb._add_conduits()


def test_multi_conduits(slb, conduit_chain_dat, tmpdir):
    expected = """first,CONDUIT,SECTION,,"Colebrook-White: [min: 0.0, max: 4.0]",h: 65.00 x w: 150.00 x l: 10.00 (Total length between first and fifth: 40.0m),,
second,CONDUIT,SECTION,,"Colebrook-White: [min: 0.0, max: 4.0]",h: 65.00 x w: 150.00 x l: 10.00,,
third,CONDUIT,SECTION,,"Colebrook-White: [min: 0.0, max: 4.0]",h: 65.00 x w: 150.00 x l: 10.00,,
fourth,CONDUIT,SECTION,,"Colebrook-White: [min: 0.0, max: 4.0]",h: 65.00 x w: 150.00 x l: 10.00,,
fifth,CONDUIT,SECTION,,"Colebrook-White: [min: 0.0, max: 4.0]",h: 65.00 x w: 150.00 x l: 0.00,,
"""

    slb._dat = conduit_chain_dat
    tmp_csv = Path(tmpdir) / "test_multi_conduits.csv"
    print(tmp_csv)
    with tmp_csv.open("w", newline="") as file:
        slb._writer = csv.writer(file)
        slb._add_conduits()

    with open(tmp_csv) as read_file:
        text = read_file.read()

    assert text == expected


def test_full_dat_from_python(slb, tmpdir, ex18_dat_path, ex18_dat_expected):
    # these two tests should be as described in the toolbox documentation

    # Im not sure if this is slightly redundant compared to test from commandline
    tmp_csv = Path(tmpdir) / "test_full_dat_from_python.csv"
    StructureLog.run(input_path=ex18_dat_path, output_path=tmp_csv)

    with open(tmp_csv) as read_file:
        text = read_file.read()
    assert text == ex18_dat_expected


def test_full_dat_from_commandline(slb, tmpdir, ex18_dat_path, ex18_dat_expected):
    # these two tests should be as described in the toolbox documentation
    tmp_csv = Path(tmpdir) / "test_full_dat_from_python.csv"
    subprocess.call(f'fmapi-structure_log --input_path "{ex18_dat_path}" --output_path "{tmp_csv}"')

    with open(tmp_csv) as read_file:
        text = read_file.read()
    assert text == ex18_dat_expected


def test_add_structures(slb, structure, tmpdir):
    slb._dat = DAT()
    structure.soffit = 3
    structure.weir_coefficient = 1
    structure.data = pd.DataFrame(data={"X": [0, 0], "Y": [0, 0]})
    structure.section_data = pd.DataFrame(data={"X": [0, 0], "Y": [0, 0], "Mannings n": [0, 0]})
    structure.opening_data = pd.DataFrame(
        data={"Start": 0, "Finish": 0, "Springing Level": 0, "Soffit Level": 0},
        index=[0],
    )
    structure.crest_elevation = 1
    structure.weir_breadth = 1
    structure.weir_length = 1
    structure.weir_elevation = 1
    slb._dat.structures["test_structure_orifice"] = structure
    struc_spill = copy.deepcopy(structure)
    struc_spill._unit = "SPILL"
    slb._dat.structures["test_structure_spill"] = struc_spill
    struc_sluice = copy.deepcopy(structure)
    struc_sluice._unit = "SLUICE"
    slb._dat.structures["test_structure_sluice"] = struc_sluice
    struc_rnweir = copy.deepcopy(structure)
    struc_rnweir._unit = "RNWEIR"
    slb._dat.structures["test_structure_rnweir"] = struc_rnweir
    struc_weir = copy.deepcopy(structure)
    struc_weir._unit = "WEIR"
    slb._dat.structures["test_structure_weir"] = struc_weir
    struc_bridge = copy.deepcopy(structure)
    struc_bridge._unit = "BRIDGE"
    slb._dat.structures["test_structure_bridge"] = struc_bridge
    struc_none = copy.deepcopy(structure)
    struc_none._unit = "NONE"
    slb._dat.structures["test_structure_none"] = struc_none

    tmp_csv = Path(tmpdir) / "temp_structure_data.csv"
    with tmp_csv.open("w") as file:
        slb._writer = csv.writer(file)
        slb._add_structures()


if __name__ == "__main__":
    pytest.main([__file__ + "::test_multi_conduits"])
