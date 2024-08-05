"""Tests to check the class HydrographPlus"""

import os
from pathlib import Path

import pandas as pd
import pytest

from floodmodeller_api.hydrology_plus.hydrograph import HydrographPlusExport


@pytest.fixture()
def metada_csv():
    """To extract the metadata from the csv to be compared with the class"""

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
def dataframe_csv():
    """To extract the df with all the flows to be compared with the df of the class"""
    test_workspace = Path(os.path.dirname(__file__), "test_data")

    return pd.read_csv(test_workspace / "df_flows_hplus.csv", index_col=0)


@pytest.fixture()
def event_csv():
    """To extract the event from the original csv to be compared with the output of the class"""
    test_workspace = Path(os.path.dirname(__file__), "test_data")

    event_file = pd.read_csv(test_workspace / "event_hplus.csv", index_col=0)
    event_series = event_file["2020 Upper - 11 - 1 - Flow (m3/s)"]
    event_series.name = "2020 Upper - 11 - 1 - Flow (m3/s)"

    return event_series


@pytest.fixture()
def hydrographplus_object():
    """To create the object to make the comparison with the csv data"""

    return HydrographPlusExport(
        Path(os.path.dirname(__file__), r"test_data/Baseline_unchecked.csv"),
    )


def test_data_metadata(metada_csv: dict[str, str], hydrographplus_object: HydrographPlusExport):
    """To compare the metada between the csv and the class"""
    assert metada_csv == hydrographplus_object.metadata


def test_data_flows_df(dataframe_csv: pd.DataFrame, hydrographplus_object: HydrographPlusExport):
    """To compare the df with all the flows between the csv and the class"""
    pd.testing.assert_frame_equal(dataframe_csv, hydrographplus_object.data_flows)


def test_data_event(event_csv: pd.Series, hydrographplus_object: HydrographPlusExport):
    """To compare the event between the csv and the class"""
    pd.testing.assert_series_equal(
        event_csv,
        hydrographplus_object.get_event("2020 Upper - 11 - 1"),
    )

