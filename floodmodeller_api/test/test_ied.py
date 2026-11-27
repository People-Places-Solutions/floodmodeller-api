from pathlib import Path

import pandas as pd
import pytest

from floodmodeller_api import IED
from floodmodeller_api.units import NCDBDY


@pytest.fixture()
def ied_fp(test_workspace):
    return Path(test_workspace, "network.ied")


@pytest.fixture()
def ied_fp_comments(test_workspace):
    return Path(test_workspace, "network_with_comments.ied")


def test_open_ied_does_not_change_file(ied_fp):
    """IED: Test str representation equal to ied file with no changes"""
    with open(ied_fp) as ied_file:
        data_before = ied_file.read()
    ied = IED(ied_fp)
    assert ied._write() == data_before
    ied = IED(ied_fp)
    cs26_expected = [
        "QTBDY",
        "CS26",
        "         4     0.000     0.000   seconds  NOEXTEND    LINEAR     0.000     0.000  OVERRIDE",
        "     1.000     0.000",
        "     1.000 46800.000",
        "     0.000 47160.000",
        "     0.000 1.000e+09",
    ]
    assert ied.boundaries["CS26"]._write() == cs26_expected


def test_ied_with_comments(ied_fp_comments):
    with open(ied_fp_comments) as ied_file:
        data_before = ied_file.read()
    ied = IED(ied_fp_comments)
    assert ied._write() == data_before


@pytest.mark.parametrize(
    ("depth_type", "slope_line", "slope_method", "slope"),
    [
        ("NORMAL", ["USER      0.00063636"], "USER", 0.00063636),
        ("CRITICAL", [], None, None),
    ],
)
def test_ncdbdy_ied_round_trip(tmp_path, depth_type, slope_line, slope_method, slope):
    path = tmp_path / "depth.ied"
    path.write_text(
        "\n".join(
            [
                "NCDBDY #revision#1 downstream test",
                f"{'DS':<12}{'':12}{'REF':<12}{'UP'}",
                depth_type,
                *slope_line,
                "         0",
                "         2     HOURS    EXTEND  OVERRIDE     0.000LINEAR",
                "     1.000     0.000",
                "     2.000     3.000",
            ],
        ),
    )
    ied = IED(path)
    boundary = ied.boundaries["DS"]
    assert isinstance(boundary, NCDBDY)
    assert boundary.depth_type == depth_type
    assert boundary.ds_reference_label == "REF"
    assert boundary.us_reference_label == "UP"
    assert boundary.slope_method == slope_method
    assert boundary.user_slope == slope
    assert boundary.override_method == "OVERRIDE"
    assert boundary.data.empty
    assert boundary.override_data.to_dict() == {0.0: 1.0, 3.0: 2.0}

    boundary.override_data.iloc[1] = 2.5
    updated = tmp_path / "depth_updated.ied"
    ied.save(updated)
    reloaded = IED(updated).boundaries["DS"]
    assert reloaded == boundary
    assert reloaded.override_data.to_dict() == {0.0: 1.0, 3.0: 2.5}
    pd.testing.assert_series_equal(reloaded.override_data, boundary.override_data)
