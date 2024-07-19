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
        ]
    )
    unit.active_data.iloc[0, 1] = 99
    assert unit.data.iloc[1, 1] == 99
    expected_row = "1.000    99.000     0.030     0.000               0.000     0.000      LEFT"
    assert expected_row in str(unit)
