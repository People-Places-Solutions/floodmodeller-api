import pandas as pd

from floodmodeller_api.units import CONDUIT


def test_create_from_blank_with_params_conduit_section():
    "Test to create a SECTION CONDUIT from blank, with parameters specified."

    coords = pd.DataFrame(
        {
            "x": [0, 1, 2],
            "y": [0, 0.5, 2],
            "cw_friction": [1.5, 1.5, 1.5],
        },
    )

    unit = CONDUIT(
        name="testing",
        spill="spill1",
        comment="Testing that the unit can be created with parameters.",
        subtype="SECTION",
        dist_to_next=5,
        coords=coords,
    )

    assert unit._write() == [
        "CONDUIT Testing that the unit can be created with parameters.",
        "SECTION",
        "testing     spill1      ",
        "         5",
        "         3",  # Number of coordinate points below
        "     0.000     0.000  1.500000",
        "     1.000     0.500  1.500000",
        "     2.000     2.000  1.500000",
    ]
