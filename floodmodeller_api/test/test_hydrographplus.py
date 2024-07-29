
import os
from pathlib import Path
import pandas as pd
from floodmodeller_api.hydrology_plus.hydrograph import HydrographPlus

import pytest


@pytest.fixture()
def load_csv_tests():
    """To load the csv with the data to be compared with the class"""
    test_workspace = Path(os.path.dirname(__file__), "test_data")
    return pd.read_csv(test_workspace / "Baseline_unchecked.csv", header=None)


@pytest.fixture()
def get_metada_csv(load_csv_tests):
    """To extract the metada from the csv to be compared with the class"""
    metadata_row_index = load_csv_tests.index[
        load_csv_tests.apply(lambda row: row.str.contains("Return Period")).any(axis=1)
    ][0]
    metadata_df = load_csv_tests.iloc[1:metadata_row_index, 0:1]

    return {row.split("=")[0]: row.split("=")[1] for row in metadata_df.iloc[:, 0]}


@pytest.fixture()
def get_datafame_csv(load_csv_tests):
    """To extract the df with all the flows to be compared with the df of the class"""
    time_row_index = load_csv_tests.index[
        load_csv_tests.apply(lambda row: row.str.contains(r"Time \(hours\)")).any(axis=1)
    ][0]
    load_csv_tests.columns = load_csv_tests.iloc[time_row_index]
    df_events = load_csv_tests.iloc[time_row_index + 1 :].reset_index(drop=True)
    df_events.columns = load_csv_tests.columns
    for col in df_events.columns[1:]:
        df_events[col] = pd.to_numeric(df_events[col], errors="coerce")

    return df_events


@pytest.fixture()
def get_event_csv(get_datafame_csv, event="2020 Upper - 11 - 1"):
    """To extract the event from the original csv to be compared with the output of the class"""
    def _remove_string_from_list_items(lst, string) -> list[str]:
        return [item.replace(string, "") for item in lst]

    def _find_index(lst, string) -> int:
        for i, item in enumerate(lst):
            if string in item:
                return i
        return -1

    index_columns = _remove_string_from_list_items(get_datafame_csv.columns, " - Flow (m3/s)")
    index_event = _find_index(index_columns, event)
    column_index = [0, index_event]

    return get_datafame_csv.iloc[:, column_index]


@pytest.fixture()
def create_hydrographplus_object(load_csv_tests):
    """To create the object to make the comparison with the csv data"""
    hydro_obj = HydrographPlus(load_csv_tests)

    return hydro_obj


def test_data_metada(get_metada_csv, create_hydrographplus_object):
    """To compare the metada between the csv and the class"""
    assert get_metada_csv == create_hydrographplus_object.metada


def test_data_flows_df(get_datafame_csv, create_hydrographplus_object):
    """To compare the df with all the flows between the csv and the class"""
    assert get_metada_csv == create_hydrographplus_object.data_flows 


def test_data_event(event="2020 Upper - 11 - 1", get_event_csv, create_hydrographplus_object):
    """To compare the event between the csv and the class"""
    assert get_metada_csv == create_hydrographplus_object.get_event(event)



