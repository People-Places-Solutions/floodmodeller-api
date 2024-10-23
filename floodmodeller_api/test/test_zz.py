# type: ignore
# ignored because the output from _ZZ.to_dataframe() is only a series in special cases

from pathlib import Path

import pandas as pd
import pytest

from floodmodeller_api import IEF, ZZN, ZZX


@pytest.fixture
def zzn(test_workspace: Path) -> ZZN:
    path = test_workspace / "network.zzn"
    return ZZN(path)


@pytest.fixture
def zzx(test_workspace: Path) -> ZZX:
    path = test_workspace / "network.zzx"
    return ZZX(path)


@pytest.fixture
def ief(test_workspace: Path) -> IEF:
    path = test_workspace / "network.ief"
    return IEF(path)


@pytest.fixture
def folder(test_workspace: Path) -> Path:
    return test_workspace / "tabular_csv_outputs"


@pytest.mark.parametrize(
    ("csv", "file"),
    [
        ("network_zzn_max.csv", "zzn"),
        ("network_zzx_max.csv", "zzx"),
    ],
)
def test_zzn_max(zzn: ZZN, zzx: ZZX, folder: Path, tmp_path: Path, csv: str, file: str):
    file_obj = zzn if file == "zzn" else zzx

    test_output_path = tmp_path / "test_output.csv"
    file_obj.export_to_csv(result_type="max", save_location=test_output_path)
    actual = pd.read_csv(test_output_path).round(3)

    expected = pd.read_csv(folder / csv)

    pd.testing.assert_frame_equal(actual, expected, rtol=0.0001, check_dtype=False)


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
    file_obj = zzn if file == "zzn" else zzx
    suffix = f"_{variable}"
    expected = pd.read_csv(folder / csv, index_col=0)

    actual_1 = file_obj.to_dataframe(variable=variable)
    actual_1.index = actual_1.index.round(3)
    pd.testing.assert_frame_equal(actual_1, expected, rtol=0.01, check_dtype=False)

    actual_2 = file_obj.to_dataframe()[variable]
    actual_2.index = actual_2.index.round(3)
    pd.testing.assert_frame_equal(actual_2, expected, rtol=0.01, check_dtype=False)

    actual_3 = file_obj.to_dataframe(multilevel_header=False).filter(like=suffix, axis=1)
    actual_3.index = actual_3.index.round(3)
    actual_3.columns = [x.removesuffix(suffix) for x in actual_3.columns]
    pd.testing.assert_frame_equal(actual_3, expected, rtol=0.01, check_dtype=False)

    actual_4 = file_obj.to_dataframe(variable=variable, multilevel_header=False)
    actual_4.index = actual_4.index.round(3)
    actual_4.columns = [x.removesuffix(suffix) for x in actual_4.columns]
    pd.testing.assert_frame_equal(actual_4, expected, rtol=0.01, check_dtype=False)


def test_zzn_include_time(zzn: ZZN):
    df = zzn.to_dataframe(result_type="max", variable="flow", include_time=True)
    actual = df.loc["resin", ["Max Flow", "Max Flow Time(hrs)"]].to_numpy()
    assert actual[0] == pytest.approx(7.296, abs=0.001)
    assert actual[1] == 9


def test_zzn_from_ief(zzn: ZZN, ief: IEF):
    zzn_df = zzn.to_dataframe()
    zzn_from_ief = ief.get_results().to_dataframe()
    pd.testing.assert_frame_equal(zzn_df, zzn_from_ief)


if __name__ == "__main__":
    pytest.main([__file__, "-s"])
