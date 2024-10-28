from pathlib import Path

import pandas as pd
import pytest

from floodmodeller_api.ief import FlowTimeProfile


@pytest.fixture()
def valid_raw_strings():
    return [
        ',,4,"fmfile.csv",fm1,T=100,"SingleEvent,AllNodes"',
        'label1,5,4,"fmfile.csv",fm1,T=100,"SingleEvent,SingleNode"',
        'label1 label2,5 6,4,"fmfile.csv",fm2,T=100,MultiEvent&Nodes',
        'label1,9,2,"ReFH2.csv",refh2,T=100',
        'label1,5,4,"fsu.csv",fsu,T=100,"Total flow m3/s (1 year)- urbanised model"',
        r'Welches_Dam,12,23,"C:\Users\ka007155\Downloads\Baseline unchecked.csv",hplus,1 - 11 - 2020 Upper',
    ]


@pytest.mark.parametrize(
    ("raw_string", "expected"),
    [
        (
            ',,4,"fmfile.csv",fm1,T=100,"SingleEvent,AllNodes"',
            {
                "labels": [],
                "columns": [],
                "start_row": 4,
                "csv_filepath": "fmfile.csv",
                "file_type": "fm1",
                "profile": "T=100",
                "comment": '"SingleEvent,AllNodes"',
            },
        ),
        (
            'label1,5,4,fmfile.csv,fm1,T=100,"SingleEvent,SingleNode"',
            {
                "labels": ["label1"],
                "columns": [5],
                "start_row": 4,
                "csv_filepath": "fmfile.csv",
                "file_type": "fm1",
                "profile": "T=100",
                "comment": '"SingleEvent,SingleNode"',
            },
        ),
    ],
)
def test_parse_raw_string(raw_string, expected):
    flow_profile = FlowTimeProfile(raw_string=raw_string)

    assert flow_profile.labels == expected["labels"]
    assert flow_profile.columns == expected["columns"]
    assert flow_profile.start_row == expected["start_row"]
    assert flow_profile.csv_filepath == expected["csv_filepath"]
    assert flow_profile.file_type == expected["file_type"]
    assert flow_profile.profile == expected["profile"]
    assert flow_profile.comment == expected["comment"]


def test_init_with_kwargs():
    kwargs = {
        "labels": ["label1", "label2"],
        "columns": [5, 6],
        "start_row": 4,
        "csv_filepath": '"fmfile.csv"',
        "file_type": "fm2",
        "profile": "T=100",
        "comment": "MultiEvent&Nodes",
        "ief_filepath": "../projects",
    }
    flow_profile = FlowTimeProfile(**kwargs)

    assert flow_profile.labels == ["label1", "label2"]
    assert flow_profile.columns == [5, 6]
    assert flow_profile.start_row == 4
    assert flow_profile.csv_filepath == '"fmfile.csv"'
    assert flow_profile.file_type == "fm2"
    assert flow_profile.profile == "T=100"
    assert flow_profile.comment == "MultiEvent&Nodes"
    assert flow_profile._csvfile == Path("../projects/fmfile.csv").resolve()


@pytest.mark.parametrize(
    "raw_string",
    [
        "label1 label2,5 6,4,fmfile.csv,fm2,T=100,MultiEvent&Nodes",
        ',,4,fmfile.csv,fm1,T=100,"SingleEvent,AllNodes"',
    ],
)
def test_str_representation(raw_string):
    flow_profile = FlowTimeProfile(raw_string=raw_string)

    assert str(flow_profile) == raw_string


def test_count_series_with_fm1(mocker):
    mocker.patch("pandas.read_csv", return_value=pd.DataFrame(columns=["A", "B", "C"]))

    kwargs = {
        "labels": ["label1"],
        "columns": [5],
        "start_row": 4,
        "csv_filepath": '"fmfile.csv"',
        "file_type": "fm1",
        "profile": "T=100",
        "comment": "SingleEvent,AllNodes",
        "ief_filepath": "../projects",
    }

    flow_profile = FlowTimeProfile(**kwargs)

    series_count = flow_profile.count_series()
    assert series_count == 3  # Since the mock CSV has 3 columns


def test_count_series_without_fm1():
    kwargs = {
        "labels": ["label1"],
        "columns": [5, 6],
        "start_row": 4,
        "csv_filepath": '"fmfile.csv"',
        "file_type": "fm2",
        "profile": "T=100",
        "comment": "MultiEvent&Nodes",
        "ief_filepath": "../projects",
    }

    flow_profile = FlowTimeProfile(**kwargs)

    series_count = flow_profile.count_series()
    assert series_count == 2  # Number of columns passed
