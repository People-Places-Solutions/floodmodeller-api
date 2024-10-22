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
def tabular_csv_outputs(test_workspace: Path) -> Path:
    return test_workspace / "tabular_csv_outputs"


def test_zzn_max(zzn: ZZN, tabular_csv_outputs: Path, tmp_path: Path):
    test_output_path = tmp_path / "test_output.csv"
    zzn.export_to_csv(result_type="max", save_location=test_output_path)
    actual = pd.read_csv(test_output_path).round(3)

    expected = pd.read_csv(tabular_csv_outputs / "network_all_max.csv")

    pd.testing.assert_frame_equal(actual, expected, rtol=0.0001, check_dtype=False)


@pytest.mark.parametrize(
    ("variable", "expected_csv"),
    [
        ("Flow", "network_flow_all.csv"),
        ("Stage", "network_stage_all.csv"),
        ("Froude", "network_fr_all.csv"),
        ("Velocity", "network_velocity_all.csv"),
        ("Mode", "network_mode_all.csv"),
        ("State", "network_state_all.csv"),
    ],
)
def test_zzn_all_timesteps(zzn: ZZN, tabular_csv_outputs: Path, variable: str, expected_csv: str):
    actual_1 = zzn.to_dataframe(variable=variable)
    actual_1.index = actual_1.index.round(3)

    actual_2 = zzn.to_dataframe()[variable]
    actual_2.index = actual_2.index.round(3)

    suffix = f"_{variable}"

    actual_3 = zzn.to_dataframe(multilevel_header=False).filter(like=suffix, axis=1)
    actual_3.index = actual_3.index.round(3)
    actual_3.columns = [x.removesuffix(suffix) for x in actual_3.columns]

    actual_4 = zzn.to_dataframe(variable=variable, multilevel_header=False)
    actual_4.index = actual_4.index.round(3)
    actual_4.columns = [x.removesuffix(suffix) for x in actual_4.columns]

    expected = pd.read_csv(tabular_csv_outputs / expected_csv, index_col=0)

    pd.testing.assert_frame_equal(actual_1, expected, rtol=0.01, check_dtype=False)
    pd.testing.assert_frame_equal(actual_2, expected, rtol=0.01, check_dtype=False)
    pd.testing.assert_frame_equal(actual_3, expected, rtol=0.01, check_dtype=False)
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


def test_zzx(zzx: ZZX):
    df = zzx.to_dataframe()
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-s"])
