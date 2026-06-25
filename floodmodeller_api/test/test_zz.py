# type: ignore
# ignored because the output from _ZZ.to_dataframe() is only a series in special cases

import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

from floodmodeller_api import IEF, ZZN, ZZX
from floodmodeller_api.test.util import parameterise_glob
from floodmodeller_api.util import read_file


@pytest.fixture()
def zzn(test_workspace: Path) -> ZZN:
    path = test_workspace / "network.zzn"
    return ZZN(path)


@pytest.fixture()
def zzx(test_workspace: Path) -> ZZX:
    path = test_workspace / "network.zzx"
    return ZZX(path)


@pytest.fixture()
def ief(test_workspace: Path) -> IEF:
    path = test_workspace / "network.ief"
    return IEF(path)


@pytest.fixture()
def folder(test_workspace: Path) -> Path:
    return test_workspace / "tabular_csv_outputs"


@pytest.mark.parametrize(
    ("csv", "file"),
    [
        ("network_zzn_max.csv", "zzn"),
        ("network_zzx_max.csv", "zzx"),
    ],
)
def test_max(zzn: ZZN, zzx: ZZX, folder: Path, csv: str, file: str):
    file_obj = zzn if file == "zzn" else zzx
    expected = pd.read_csv(folder / csv, index_col=0)

    actual = file_obj.to_dataframe(result_type="max")
    pd.testing.assert_frame_equal(actual, expected, atol=1e-3, check_dtype=False)


@pytest.mark.parametrize(
    ("variable", "csv", "file"),
    [
        # zzn
        ("Flow", "network_zzn_flow.csv", "zzn"),
        ("Stage", "network_zzn_stage.csv", "zzn"),
        ("Froude", "network_zzn_fr.csv", "zzn"),
        ("Velocity", "network_zzn_velocity.csv", "zzn"),
        ("Mode", "network_zzn_mode.csv", "zzn"),
        ("State", "network_zzn_state.csv", "zzn"),
        # zzx
        ("Left FP h", "network_zzx_left_fp_h.csv", "zzx"),
        ("Link inflow", "network_zzx_link_inflow.csv", "zzx"),
        ("Right FP h", "network_zzx_right_fp_h.csv", "zzx"),
        ("Right FP mode", "network_zzx_right_fp_mode.csv", "zzx"),
        ("Left FP mode", "network_zzx_left_fp_mode.csv", "zzx"),
    ],
)
def test_all_timesteps(zzn: ZZN, zzx: ZZX, folder: Path, variable: str, csv: str, file: str):
    """
    This test compares data extracted from ZZN/ZZX files against known values from .csv.

    Multiple assertions used to test various different methods to access variable results

    """
    zz_obj = zzn if file == "zzn" else zzx
    suffix = f"_{variable}"
    expected = pd.read_csv(folder / csv, index_col=0)

    actual_1 = zz_obj.to_dataframe(variable=variable)
    actual_1.index = actual_1.index.round(3)
    pd.testing.assert_frame_equal(actual_1, expected, atol=1e-3, check_dtype=False)

    actual_2 = zz_obj.to_dataframe()[variable]
    actual_2.index = actual_2.index.round(3)
    pd.testing.assert_frame_equal(actual_2, expected, atol=1e-3, check_dtype=False)

    actual_3 = zz_obj.to_dataframe(multilevel_header=False).filter(like=suffix, axis=1)
    actual_3.index = actual_3.index.round(3)
    actual_3.columns = [x.removesuffix(suffix) for x in actual_3.columns]
    pd.testing.assert_frame_equal(actual_3, expected, atol=1e-3, check_dtype=False)

    actual_4 = zz_obj.to_dataframe(variable=variable, multilevel_header=False)
    actual_4.index = actual_4.index.round(3)
    actual_4.columns = [x.removesuffix(suffix) for x in actual_4.columns]
    pd.testing.assert_frame_equal(actual_4, expected, atol=1e-3, check_dtype=False)


def test_zzn_include_time(zzn: ZZN):
    zzn_df = zzn.to_dataframe(result_type="max", variable="flow", include_time=True)
    actual = zzn_df.loc["resin", ["Max Flow", "Max Flow Time(hrs)"]].to_numpy()
    assert actual[0] == pytest.approx(7.296, abs=0.001)
    assert actual[1] == 9


def test_zzn_from_ief(zzn: ZZN, ief: IEF):
    zzn_df = zzn.to_dataframe()
    zzn_from_ief = ief.get_results().to_dataframe()
    pd.testing.assert_frame_equal(zzn_df, zzn_from_ief)


def test_zzn_to_csv(zzn: ZZN, tmp_path: Path, test_workspace: Path):
    # default
    zzn.export_to_csv()
    path = test_workspace / "network.csv"
    assert path.exists()
    path.unlink()

    # absolute
    zzn.export_to_csv(tmp_path / "test.csv")
    path = tmp_path / "test.csv"
    assert path.exists()
    path.unlink()

    # relative
    zzn.export_to_csv("test.csv")
    path = zzn.filepath.parent / "test.csv"
    assert path.exists()
    path.unlink()

    # folder
    zzn.export_to_csv(tmp_path)
    path = tmp_path / "network.csv"
    assert path.exists()
    path.unlink()

    # doesn't exist
    zzn.export_to_csv("test")
    path = test_workspace / "test/network.csv"
    assert path.exists()
    path.unlink()


def test_meta_is_read_only(zzx: ZZN):
    assert dict(zzx.meta) == zzx._meta

    with pytest.raises(TypeError):
        zzx.meta["variables"] = "hi"

    zzx._meta["variables"] = "hi"


@pytest.mark.parametrize("simulation_case", ["zero_start", "negative_start", "positive_start"])
@pytest.mark.parametrize("file_type", ["zzn", "zzx"])
def test_zz_reads_correct_start_end(test_workspace, simulation_case, file_type):
    """
    This test compares that the dataframe produced by _ZZ classes matches what we expect from the corresponding IEF that produced the results.

    Compares start and finish times to first and last indecies of df,
    Also checks that the number of rows matches what we expect based on the save interval.
    """
    ief_filepath = test_workspace / simulation_case / f"{simulation_case}.ief"
    ief = IEF(ief_filepath)

    zz_filepath = test_workspace / simulation_case / f"{simulation_case.upper()}.{file_type}"
    zz: ZZN | ZZX = read_file(zz_filepath)
    zz_df = zz.to_dataframe()

    assert zz_df.index[0] == ief.start
    assert zz_df.index[-1] == ief.finish

    # We expect saving to happen on both the first and last timestep, hence the `+1`
    expected_rows = ((ief.finish - ief.start) * (3600 / ief.saveinterval)) + 1
    assert len(zz_df.index) == expected_rows


@pytest.mark.parametrize("simulation_case", ["zero_start", "negative_start", "positive_start"])
@pytest.mark.parametrize(("file_type", "variable"), [("zzn", "Flow"), ("zzx", "Link inflow")])
def test_result_type_max_matches_full_df(test_workspace, simulation_case, file_type, variable):
    """
    Tests `result_type="max"` option of `to_dataframe()` for consistency with main dataframe output.

    This should catch any issues where the time is not picked up properly in the max output here.
    """

    zz_filepath = test_workspace / simulation_case / f"{simulation_case.upper()}.{file_type}"
    zz: ZZN | ZZX = read_file(zz_filepath)
    zz_df = zz.to_dataframe()

    zz_max_df = zz.to_dataframe(result_type="max", include_time=True)
    units_to_check = ["M040", "M042", "M054"]

    for label in units_to_check:
        max_flow = zz_df[variable][label].max()
        max_flow_time = zz_df[variable][label].idxmax()
        assert zz_max_df.loc[label, f"Max {variable}"] == pytest.approx(max_flow, 0.001)
        assert zz_max_df.loc[label, f"Max {variable} Time(hrs)"] == max_flow_time


@pytest.mark.parametrize(
    "zz_path",
    parameterise_glob("zz_gc/**/*.zzn") + parameterise_glob("zz_gc/**/*.zzx"),
    ids=lambda zz_path: zz_path.parent.name + zz_path.suffix,
)
def test_zz_gc_fatal_error(test_workspace, zz_path):
    """
    Test whether ZZ classes can load results without causing the fatal error attributed to Python garbage collection.

    Manifests as 'Windows fatal exception: access violation' on Windows and
    'Fatal Python error: Segmentation fault' on Linux.

    This test runs in subprocess as running it directly in the test suite will crash all other ongoing tests
    and is repeated to attempt to trigger the error if it is intermittent."""
    zz_type = "ZZN" if zz_path.suffix == ".zzn" else "ZZX"
    for _ in range(10):
        code = f"""
from floodmodeller_api import {zz_type}
zz_type = {zz_type}
zz_obj = zz_type(r'{test_workspace / zz_path}')
assert isinstance(zz_obj, zz_type)
"""
        result = subprocess.run([sys.executable, "-c", code], capture_output=True)
        assert result.returncode == 0, (
            f"Process crashed with return code {result.returncode}\nstderr: {result.stderr.decode()}"
        )
