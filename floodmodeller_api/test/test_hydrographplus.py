"""Tests to check the class HydrographPlus"""
import os
from pathlib import Path

import pandas as pd
import pytest

from floodmodeller_api.hydrology_plus.hydrograph import HydrographPlus


# @pytest.fixture()
# def csv_tests():
#     """To load the csv with the data to be compared with the class"""
#     test_workspace = Path(os.path.dirname(__file__), "test_data")

#     return pd.read_csv(test_workspace / "Baseline_unchecked.csv", header=None)


@pytest.fixture()
def metada_csv():
    """To extract the metadata from the csv to be compared with the class"""

    return {"Hydrograph Name":"Baseline unchecked",
            "Hydrograph Description":"",
            "Calculation Point":"CP_003",
            "ReFH2 Name":"CP_003_ReFH2_1",
            "Winfap Name":"CP_003_WINFAP_1",
            "Urban/Rural":"Urban",
            "Urban/Rural Comment":"",
            "ReFH2 Comment":"",
            "Winfap Comment":"",
            "Winfap Distribution":"GEV",
            "Winfap Distribution Comment":"",
            "Use Climate Change Allowances":"True",
            "Use Custom Scale Factors":"False",
            "Created By":"KA007155",
            "Created Date":"30/04/2024 09:42:23",
            "Checksum":"ef77d9bd-2eb3-4689-a1e3-665d293db810"
            }


@pytest.fixture()
def dataframe_csv():
    """To extract the df with all the flows to be compared with the df of the class"""
    test_workspace = Path(os.path.dirname(__file__), "test_data")

    return pd.read_csv(test_workspace / "df_flows_hplus.csv", header=None)


# @pytest.fixture()
# def event_csv(datafame_csv, event="2020 Upper - 11 - 1"):
#     """To extract the event from the original csv to be compared with the output of the class"""
#     def _remove_string_from_list_items(lst, string) -> list[str]:
#         return [item.replace(string, "") for item in lst]

#     def _find_index(lst, string) -> int:
#         for i, item in enumerate(lst):
#             if string in item:
#                 return i
#         return -1

#     index_columns = _remove_string_from_list_items(datafame_csv.columns, " - Flow (m3/s)")
#     index_event = _find_index(index_columns, event)
#     column_index = [0, index_event]

#     return datafame_csv.iloc[:, column_index]


@pytest.fixture()
def hydrographplus_object():
    """To create the object to make the comparison with the csv data"""

    return HydrographPlus(Path(os.path.dirname(__file__), r"test_data\Baseline_unchecked.csv"))


def test_data_metadata(metada_csv, hydrographplus_object):
    """To compare the metada between the csv and the class"""
    assert metada_csv == hydrographplus_object.metadata


def test_data_flows_df(dataframe_csv, hydrographplus_object):
    """To compare the df with all the flows between the csv and the class"""
    df_csv_reset = dataframe_csv.reset_index(drop=True)
    df_obj_reset = hydrographplus_object.data_flows.reset_index(drop=True)
    
    df_csv_sorted = df_csv_reset.sort_values(by=df_csv_reset.columns.tolist()).reset_index(drop=True)
    df_obj_sorted = df_obj_reset.sort_values(by=df_obj_reset.columns.tolist()).reset_index(drop=True)
    assert df_csv_sorted.equals(df_obj_sorted)


# def test_data_event(event_csv, hydrographplus_object, event="2020 Upper - 11 - 1"):
#     """To compare the event between the csv and the class"""
#     assert event_csv.equals(hydrographplus_object.get_event(event))



