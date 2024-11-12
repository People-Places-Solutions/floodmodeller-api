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


@pytest.fixture()
def slb():
    return StructureLogBuilder("", "")


@pytest.fixture()
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
    c.elevation_invert = 0
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


@pytest.fixture()
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
    c.elevation_invert = 3
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


@pytest.fixture()
def no_length():
    return 0


@pytest.fixture()
def with_length():
    return 4.973


@pytest.fixture()
def structure():
    return ORIFICE()


@pytest.fixture()
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


@pytest.fixture()
def ex18_dat_path(test_workspace):
    return Path(test_workspace, "EX18.DAT")


@pytest.fixture()
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


def test_empty_conduit(slb, conduit_empty):
    slb._dat = DAT()
    output, _ = slb._conduit_data(conduit_empty)
    assert output == {
        "length": 0.0,
        "total_length": 0.0,
    }


def test_multi_conduits(slb, conduit_chain_dat, tmpdir):
    expected = """Unit Name,Unit Type,Unit Subtype,Comment,Friction,Dimensions (m),Weir Coefficient,Culvert Inlet/Outlet Loss
first,CONDUIT,SECTION,,"Colebrook-White: [min: 0.000, max: 4.000]",h: 65.00 x w: 156.00 x l: 10.00 (Total conduit length: 40.00),,
second,CONDUIT,SECTION,,"Colebrook-White: [min: 0.000, max: 4.000]",h: 65.00 x w: 156.00 x l: 10.00,,
third,CONDUIT,SECTION,,"Colebrook-White: [min: 0.000, max: 4.000]",h: 65.00 x w: 156.00 x l: 10.00,,
fourth,CONDUIT,SECTION,,"Colebrook-White: [min: 0.000, max: 4.000]",h: 65.00 x w: 156.00 x l: 10.00,,
fifth,CONDUIT,SECTION,,"Colebrook-White: [min: 0.000, max: 4.000]",h: 65.00 x w: 156.00 x l: 0.00,,
"""

    slb._dat = conduit_chain_dat
    tmp_csv = Path(tmpdir) / "test_multi_conduits.csv"
    with tmp_csv.open("w", newline="") as file:
        slb._writer = csv.writer(file)
        slb._add_conduits()
        slb._write_csv_output(file)

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
