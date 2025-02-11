import pandas as pd
import pytest

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


@pytest.mark.parametrize("river_unit_data", [x[0] for x in river_unit_data_cases])
def test_read_write(river_unit_data):
    river_section_1 = RIVER(river_unit_data)
    river_section_2 = RIVER(river_section_1._write())
    assert river_section_1 == river_section_2


@pytest.mark.parametrize(("river_unit_data", "expected_len"), river_unit_data_cases)
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
