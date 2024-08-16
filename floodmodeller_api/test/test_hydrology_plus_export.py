"""Tests to check the class HydrographPlus"""

import os
from pathlib import Path

import pandas as pd
import pytest

from floodmodeller_api.hydrology_plus.hydrology_plus_export import HydrologyPlusExport


@pytest.fixture()
def expected_metadata():
    """Extracts the metadata from the csv to be compared with the class"""

    return {
        "Hydrograph Name": "Baseline unchecked",
        "Hydrograph Description": "",
        "Calculation Point": "CP_003",
        "ReFH2 Name": "CP_003_ReFH2_1",
        "Winfap Name": "CP_003_WINFAP_1",
        "Urban/Rural": "Urban",
        "Urban/Rural Comment": "",
        "ReFH2 Comment": "",
        "Winfap Comment": "",
        "Winfap Distribution": "GEV",
        "Winfap Distribution Comment": "",
        "Use Climate Change Allowances": "True",
        "Use Custom Scale Factors": "False",
        "Created By": "KA007155",
        "Created Date": "30/04/2024 09:42:23",
        "Checksum": "ef77d9bd-2eb3-4689-a1e3-665d293db810",
    }


@pytest.fixture()
def expected_dataframe(test_workspace):
    """Extracts the df with all the flows to be compared with the df of the class"""

    return pd.read_csv(test_workspace / "df_flows_hplus.csv", index_col=0)


@pytest.fixture()
def expected_event(test_workspace):
    """Extracts the event from the original csv to be compared with the output of the class"""
    event_file = pd.read_csv(test_workspace / "event_hplus.csv", index_col=0)

    return event_file.squeeze()


@pytest.fixture()
def hydrology_plus_export_object():
    """Creates the object to make the comparison with the csv data"""

    return HydrologyPlusExport(
        Path(os.path.dirname(__file__), r"test_data/Baseline_unchecked.csv"),
    )


def test_data_metadata(
    expected_metadata: dict[str, str],
    hydrology_plus_export_object: HydrologyPlusExport,
):
    """Compares the metadata between the csv and the class"""
    assert expected_metadata == hydrology_plus_export_object.metadata


def test_data_flows_df(
    expected_dataframe: pd.DataFrame,
    hydrology_plus_export_object: HydrologyPlusExport,
):
    """Compares the df with all the flows between the csv and the class"""
    pd.testing.assert_frame_equal(expected_dataframe, hydrology_plus_export_object.data)


def test_data_event(expected_event: pd.Series, hydrology_plus_export_object: HydrologyPlusExport):
    """Compares the event between the csv and the class"""
    pd.testing.assert_series_equal(
        expected_event,
        hydrology_plus_export_object.get_event("2020 Upper - 11 - 1"),
    )


def test_data_event_from_params(
    expected_event: pd.Series,
    hydrology_plus_export_object: HydrologyPlusExport,
):
    """Compares the event between the csv and the class"""
    pd.testing.assert_series_equal(
        expected_event,
        hydrology_plus_export_object.get_event(
            scenario="2020 Upper",
            storm_duration=11.0,
            return_period=1.0,
        ),
    )
