"""Tests to check the class HydrographPlus"""

from __future__ import annotations

import pandas as pd
import pytest

from floodmodeller_api.hydrology_plus.hydrology_plus_export import HydrologyPlusExport
from floodmodeller_api.ief import IEF, FlowTimeProfile
from floodmodeller_api.units import QTBDY
from floodmodeller_api.util import FloodModellerAPIError


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
def hydrology_plus_export_object(test_workspace):
    """Creates the object to make the comparison with the csv data"""

    return HydrologyPlusExport(test_workspace / "Baseline_unchecked.csv")


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
        hydrology_plus_export_object.get_event_flow("2020 Upper - 11 - 1"),
    )


def test_data_event_from_params(
    expected_event: pd.Series,
    hydrology_plus_export_object: HydrologyPlusExport,
):
    """Compares the event between the csv and the class"""
    pd.testing.assert_series_equal(
        expected_event,
        hydrology_plus_export_object.get_event_flow(
            scenario="2020 Upper",
            storm_duration=11.0,
            return_period=1.0,
        ),
    )


def test_get_unique_event_components(hydrology_plus_export_object: HydrologyPlusExport):
    """Test that unique event components are correctly extracted."""
    # Expected unique components
    expected_return_periods = sorted({1, 2, 5, 10, 30, 50, 75, 100, 200, 1000})
    expected_storm_durations = sorted({11})
    expected_scenarios = sorted({"2020 Upper", "Reconciled Baseline"})

    # Trigger the _get_unique_event_components method
    hydrology_plus_export_object._get_unique_event_components()

    # Assertions
    assert hydrology_plus_export_object.return_periods == expected_return_periods
    assert hydrology_plus_export_object.storm_durations == expected_storm_durations
    assert hydrology_plus_export_object.scenarios == expected_scenarios


def test_invalid_header_in_file(tmp_path):
    """Test that _read raises a ValueError if the file header is invalid."""
    # Create a temporary file with an invalid header
    invalid_header_file = tmp_path / "invalid_header.csv"
    invalid_header_content = "Invalid Header\nSome other content\n"
    invalid_header_file.write_text(invalid_header_content)

    with pytest.raises(FloodModellerAPIError):
        HydrologyPlusExport(invalid_header_file)


def test_gereate_ief_files(test_workspace, hydrology_plus_export_object: HydrologyPlusExport):
    iefs = hydrology_plus_export_object.generate_iefs(node_label="pytest")
    assert len(iefs) == len(hydrology_plus_export_object.data.columns)
    generated_files = list(test_workspace.glob("*_generated.ief"))
    assert len(generated_files) == len(hydrology_plus_export_object.data.columns)
    for file in generated_files:
        file.unlink()


def test_generate_ief(
    test_workspace,
    hydrology_plus_export_object: HydrologyPlusExport,
):
    """Test generating a single IEF file."""
    node_label = "test_node"
    event = "2020 Upper - 11 - 1"

    # Generate a single IEF file
    generated_ief = hydrology_plus_export_object.generate_ief(
        node_label=node_label,
        event=event,
    )

    # Assert the IEF file was created and matches expectations
    assert isinstance(generated_ief, IEF)
    assert len(generated_ief.flowtimeprofiles) == 1
    output_file = test_workspace / "2020Upper-11-1_generated.ief"
    assert output_file.exists()
    assert generated_ief.filepath == output_file

    # Cleanup
    output_file.unlink()


def test_get_qtbdy(hydrology_plus_export_object: HydrologyPlusExport, expected_event: pd.Series):
    """Test generating a QTBDY object."""
    qtbdy_name = "test_qtbdy"
    event = "2020 Upper - 11 - 1"

    # Generate a QTBDY object
    qtbdy = hydrology_plus_export_object.get_qtbdy(
        qtbdy_name=qtbdy_name,
        event=event,
    )

    # Assert the QTBDY object is created and contains expected data
    assert isinstance(qtbdy, QTBDY)
    pd.testing.assert_series_equal(qtbdy.data, expected_event)
    assert qtbdy.name == qtbdy_name

    # assert QTBDY is valid
    qtbdy._write()


def test_get_flowtimeprofile(hydrology_plus_export_object: HydrologyPlusExport):
    """Test generating a FlowTimeProfile object."""
    node_label = "test_node"
    event = "2020 Upper - 11 - 1"

    # Generate a FlowTimeProfile object
    ftp = hydrology_plus_export_object.get_flowtimeprofile(node_label=node_label, event=event)

    # Assert the FlowTimeProfile object is created and contains expected attributes
    assert isinstance(ftp, FlowTimeProfile)
    assert ftp.labels == [node_label]
    assert ftp.csv_filepath == hydrology_plus_export_object.filepath.name
    assert ftp.profile == f"{event} - Flow (m3/s)"


@pytest.mark.parametrize(
    "export_csv",
    [
        "hplus_export_example_1.csv",
        "hplus_export_example_2.csv",
        "hplus_export_example_3.csv",
        "hplus_export_example_4.csv",
        "hplus_export_example_5.csv",
        "hplus_export_example_6.csv",
        "hplus_export_example_7.csv",
        "hplus_export_example_8.csv",
        "hplus_export_example_9.csv",
        "hplus_export_example_10.csv",
    ],
)
def test_load_hydrology_plus_export_doesnt_fail(test_workspace, export_csv):
    """Ensure loading a hydrology+ export file succeeds without error"""
    HydrologyPlusExport(test_workspace / export_csv)
