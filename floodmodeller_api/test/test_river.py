import pandas as pd
import pytest

from floodmodeller_api import DAT
from floodmodeller_api.units.sections import RIVER

river_unit_data_cases = [
    (
        [
            "RIVER normal case",
            "SECTION",
            "SomeUnit",
            "     0.000            0.000100  1000.000",
            "        5",
            "     0.000        10     0.030     0.000                 0.0       0.0          ",
            "     1.000         9     0.030     0.000                 0.0       0.0      LEFT",
            "     2.000         5     0.030     0.000                 0.0       0.0          ",
            "     3.000         6     0.030     0.000                 0.0       0.0     RIGHT",
            "     4.000        10     0.030     0.000                 0.0       0.0          ",
        ],
        3,
    ),
    (
        [
            "RIVER close together",
            "SECTION",
            "AnotherUnit",
            "     0.000            0.000100  1000.000",
            "        3",
            "     0.000        15     0.040     0.000                 0.0       0.0          ",
            "     1.500         8     0.040     0.000                 0.0       0.0      LEFT",
            "     3.000        12     0.040     0.000                 0.0       0.0     RIGHT",
        ],
        2,
    ),
    (
        [
            "RIVER double markers",
            "SECTION",
            "AnotherUnit",
            "     0.000            0.000100  1000.000",
            "        3",
            "     0.000        15     0.040     0.000                 0.0       0.0          ",
            "     1.500         8     0.040     0.000                 0.0       0.0      LEFT",
            "     3.000        12     0.040     0.000                 0.0       0.0          ",
            "     4.000        13     0.040     0.000                 0.0       0.0      LEFT",
            "     5.000         2     0.040     0.000                 0.0       0.0          ",
            "     6.000         1     0.040     0.000                 0.0       0.0          ",
            "     7.000       254     0.040     0.000                 0.0       0.0     RIGHT",
            "     8.000        21     0.040     0.000                 0.0       0.0          ",
            "     9.000        76     0.040     0.000                 0.0       0.0     RIGHT",
        ],
        4,
    ),
]
river_unit_data_cases_ids = [x[0][0] for x in river_unit_data_cases]


@pytest.mark.parametrize(
    "river_unit_data",
    [x[0] for x in river_unit_data_cases],
    ids=river_unit_data_cases_ids,
)
def test_read_write(river_unit_data):
    river_section_1 = RIVER(river_unit_data)
    river_section_2 = RIVER(river_section_1._write())
    assert river_section_1 == river_section_2


@pytest.mark.parametrize(
    ("unit_name", "expected"),
    [
        (
            "UNIT041",
            {
                "subtype": "MUSKINGUM",
                "name": "UNIT041",
                "comment": "",
                "dist_to_next": 20,
                "bed_elevation": 0,
                "k": 1,
                "x": 0.5,
                "vq_method": "VQ POWER LAW",
                "min_velocity": 0,
                "flow_threshold": 10,
                "velocity_constant": 1,
                "velocity_exponent": 2,
            },
        ),
        (
            "UNIT042",
            {
                "subtype": "MUSK-XSEC",
                "name": "UNIT042",
                "comment": "",
                "first_lateral_inflow_node": "",
                "second_lateral_inflow_node": "",
                "lat1": "",
                "lat2": "",
                "lat3": "",
                "lat4": "",
                "dist_to_next": 100,
                "bed_elevation": 0,
                "slope": 0.002,
                "min_subnodes": 4,
                "max_subnodes": 98,
                "max_flow": 0.0,
                "low_flow_smoothing_factor": 0.2,
                "nrows": 3,
                "data": pd.DataFrame(
                    [
                        [0.0, 0.0, 0.03, True, 0.0, "left", 1.0, 4.0],
                        [1.0, -2.0, 0.03, False, 1.0, "", 2.0, 5.0],
                        [2.0, 0.0, 0.03, True, 1.0, "right", 3.0, 6.0],
                    ],
                    columns=[
                        "X",
                        "Y",
                        "Mannings n",
                        "Panel",
                        "RPL",
                        "Marker",
                        "Easting",
                        "Northing",
                    ],
                ),
                "location": (2.0, 5.0),
                "vq_method": "VQ SECTION",
            },
        ),
        (
            "UNIT043",
            {
                "subtype": "MUSK-VPMC",
                "name": "UNIT043",
                "comment": "",
                "first_lateral_inflow_node": "",
                "second_lateral_inflow_node": "",
                "lat1": "",
                "lat2": "",
                "lat3": "",
                "lat4": "",
                "dist_to_next": 100,
                "bed_elevation": 0,
                "slope": 0.0,
                "min_subnodes": 4,
                "max_subnodes": 98,
                "specified_discharge": 90,
                "nrows": 2,
                "wavespeed_data": pd.DataFrame(
                    [[1.0, 1.0, 0.9, 1.0], [10.0, 2.0, 0.8, 2.0]],
                    columns=["Flow", "Wavespeed", "Attenuation", "Water Level"],
                ),
                "vq_method": "VQ POWER LAW",
                "min_velocity": 0,
                "flow_threshold": 10,
                "velocity_constant": 1,
                "velocity_exponent": 2,
            },
        ),
        (
            "UNIT044",
            {
                "subtype": "MUSK-RSEC",
                "name": "UNIT044",
                "comment": "",
                "first_lateral_inflow_node": "",
                "second_lateral_inflow_node": "",
                "lat1": "",
                "lat2": "",
                "lat3": "",
                "lat4": "",
                "dist_to_next": 100,
                "bed_elevation": 1,
                "_ribaman_keyword": "RIBAMAN",
                "roughness_type": "MANNING",
                "channel_roughness": 0.02,
                "floodplain_roughness": 0.1,
                "channel_slope": 0.001,
                "floodplain_slope": 0.0001,
                "b1": 10,
                "b2": 15,
                "b3": 100,
                "b4": 12,
                "d1": 2,
                "d2": 1,
                "d3": 3,
                "d4": 0.5,
                "vs": 5,
                "max_flow": 0,
                "bankfull_proportion": 0.9,
                "vq_method": "VQ RATING",
                "vq_nrows": 3,
                "vq_data": pd.DataFrame(
                    [[0.0, 0.0], [1.0, 2.0], [2.0, 4.0]],
                    columns=["Velocity", "Flow"],
                ),
            },
        ),
    ],
)
def test_musk_read_write_from_dat(test_workspace, unit_name, expected):
    river_section_1 = DAT(test_workspace / "All Units 4_6.DAT").sections[unit_name]
    river_section_2 = RIVER(river_section_1._write())

    assert river_section_1 == river_section_2
    for attr, expected_value in expected.items():
        if isinstance(expected_value, pd.DataFrame):
            actual_value = getattr(river_section_1, attr)
            pd.testing.assert_frame_equal(actual_value, expected_value)
        else:
            assert getattr(river_section_1, attr) == expected_value


@pytest.mark.parametrize(
    ("river_unit_data", "expected_len"),
    river_unit_data_cases,
    ids=river_unit_data_cases_ids,
)
def test_river_active_data(river_unit_data, expected_len):
    river_section = RIVER(river_unit_data)
    active_data = river_section.active_data

    assert len(active_data) == expected_len
    assert active_data.iloc[0].Deactivation == "LEFT"
    assert active_data.iloc[-1].Deactivation == "RIGHT"
    assert "LEFT" not in active_data.iloc[1:-1].Deactivation.to_list()
    assert "RIGHT" not in active_data.iloc[1:-1].Deactivation.to_list()


def test_edit_active_data():
    unit = RIVER(
        [
            "RIVER normal case",
            "SECTION",
            "SomeUnit",
            "     0.000            0.000100  1000.000",
            "        5",
            "     0.000        10     0.030     0.000                 0.0       0.0          ",
            "     1.000         9     0.030     0.000                 0.0       0.0      LEFT",
            "     2.000         5     0.030     0.000                 0.0       0.0          ",
            "     3.000         6     0.030     0.000                 0.0       0.0     RIGHT",
            "     4.000        10     0.030     0.000                 0.0       0.0          ",
        ],
    )
    unit.active_data.iloc[0, 1] = 99
    assert unit.data.iloc[1, 1] == 99
    expected_row = "1.000    99.000     0.030     0.000               0.000     0.000      LEFT"
    assert expected_row in str(unit)


def test_active_data_with_no_markers():
    unit = RIVER(
        [
            "RIVER normal case",
            "SECTION",
            "SomeUnit",
            "     0.000            0.000100  1000.000",
            "        5",
            "     0.000        10     0.030",
            "     1.000         9     0.030",
            "     2.000         5     0.030",
            "     3.000         6     0.030",
            "     4.000        10     0.030",
        ],
    )
    assert len(unit.active_data) == 5
    unit.data.iloc[1, 8] = "LEFT"
    unit.data.iloc[3, 8] = "RIGHT"
    assert len(unit.active_data) == 3


def test_create_from_blank():
    blank_unit = RIVER()
    assert len(blank_unit.data) == 0
    assert len(blank_unit.active_data) == 0
    assert blank_unit._write() == [
        "RIVER",
        "SECTION",
        "new_section                                                                         ",
        "     0.000            0.000100  1000.000",
        "         0",
    ]


def test_create_from_blank_with_params():
    unit = RIVER(
        name="for_test",
        comment="testing",
        spill1="t",
        spill2="e",
        lat1="s",
        lat2="t",
        lat3="i",
        lat4="ng",
        dist_to_next=55,
        slope=0.00015,
        density=1010.0,
        data=pd.DataFrame(
            {
                "X": [0.0, 1.0, 2.0],
                "Y": [5.0, 2.0, 5.0],
                "Mannings n": [0.01, 0.01, 0.01],
                "Panel": ["", "", ""],
                "RPL": [0.0, 0.0, 0.0],
                "Marker": ["", "", ""],
                "Easting": [0.0, 0.0, 0.0],
                "Northing": [0.0, 0.0, 0.0],
                "Deactivation": ["", "", ""],
                "SP. Marker": ["", "", ""],
            },
        ),
    )

    assert unit._write() == [
        "RIVER testing",
        "SECTION",
        "for_test    t           e           s           t           i           ng          ",
        "    55.000            0.000150  1010.000",
        "         3",
        "     0.000     5.000     0.010     0.000               0.000     0.000                    ",
        "     1.000     2.000     0.010     0.000               0.000     0.000                    ",
        "     2.000     5.000     0.010     0.000               0.000     0.000                    ",
    ]


def test_set_river_dataframe_correct():
    unit = RIVER(
        [
            "RIVER normal case",
            "SECTION",
            "SomeUnit",
            "     0.000            0.000100  1000.000",
            "        5",
            "     0.000        10     0.030",
            "     1.000         9     0.030",
            "     2.000         5     0.030",
            "     3.000         6     0.030",
            "     4.000        10     0.030",
        ],
    )

    inputs = pd.DataFrame(
        {
            "X": [0.0, 1.0, 2.0],
            "Y": [5.0, 2.0, 5.0],
            "Mannings n": [0.01, 0.01, 0.01],
            "Panel": ["", "", ""],
            "RPL": [0.0, 0.0, 0.0],
            "Marker": ["", "", ""],
            "Easting": [0.0, 0.0, 0.0],
            "Northing": [0.0, 0.0, 0.0],
            "Deactivation": ["", "", ""],
            "SP. Marker": ["", "", ""],
        },
    )

    unit.data = inputs.copy()
    pd.testing.assert_frame_equal(unit._data, inputs.copy())


def test_set_river_dataframe_incorrect():
    unit = RIVER()

    inputs = pd.DataFrame(
        {
            "X": [0.0, 1.0, 2.0],
            "Y": [5.0, 2.0, 5.0],
            "Mannings n": [0.01, 0.01, 0.01],
            "RPL": [0.0, 0.0, 0.0],
            "Marker": ["", "", ""],
            "Easting": [0.0, 0.0, 0.0],
            "Deactivation": ["", "", ""],
            "SP. Marker": ["", "", ""],
        },
    )

    with pytest.raises(ValueError, match="The DataFrame must only contain columns"):
        unit.data = inputs.copy()


def test_set_river_dataframe_case_sensitivity():
    unit = RIVER()

    inputs = pd.DataFrame(
        {
            "x": [0.0, 1.0, 2.0],
            "Y": [5.0, 2.0, 5.0],
            "mANNINGs n": [0.01, 0.01, 0.01],
            "Panel": ["", "", ""],
            "RPL": [0.0, 0.0, 0.0],
            "Marker": ["", "", ""],
            "Easting": [0.0, 0.0, 0.0],
            "Northing": [0.0, 0.0, 0.0],
            "Deactivation": ["", "", ""],
            "SP. Marker": ["", "", ""],
        },
    )

    unit.data = inputs.copy()
    pd.testing.assert_frame_equal(unit._data, inputs.copy())
