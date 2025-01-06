"""
Flood Modeller Python API
Copyright (C) 2025 Jacobs U.K. Limited

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see https://www.gnu.org/licenses/.

If you have any query about this program or this License, please contact us at support@floodmodeller.com or write to the following
address: Jacobs UK Limited, Flood Modeller, Cottons Centre, Cottons Lane, London, SE1 2QG, United Kingdom.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .._base import FMFile
from ..ief import IEF, FlowTimeProfile
from ..units import QTBDY
from ..util import handle_exception


class HydrologyPlusExport(FMFile):
    """Class to handle the exported output of Hydrology +

    Args:
        csv_file_path (str | Path): produced by Hydrology + in Flood Modeller

    Output:
        Initiates 'HydrologyPlusExport' object
        The event/s needed to run simulations in Flood Modeller
    """

    _filetype: str = "HydrologyPlusExport"
    _suffix: str = ".csv"

    @handle_exception(when="read")
    def __init__(self, csv_file_path: str | Path, from_json: bool = False):
        if from_json:
            return
        FMFile.__init__(self, csv_file_path)
        self._read()

    def _read(self):
        with self._filepath.open("r") as file:
            header = file.readline().strip(" ,\n\r")
            if header != "Flood Modeller Hydrology+ hydrograph file":
                msg = "Input file is not the correct format for Hydrology+ export data."
                raise ValueError(msg)

        self._data_file = pd.read_csv(self._filepath)
        self._metadata = self._get_metadata()
        self._data = self._get_df_hydrographs_plus()
        self._get_unique_event_components()

    def _get_metadata(self) -> dict[str, str]:
        """Extracts the metada from the hydrology + results"""
        metadata_row_index = self._data_file.index[self._data_file.iloc[:, 0] == "Return Period"][0]
        metadata_df = self._data_file.iloc[:metadata_row_index, 0].tolist()

        return dict([row.split("=") for row in metadata_df if isinstance(row, str)])

    def _get_df_hydrographs_plus(self) -> pd.DataFrame:
        """Extracts all the events generated in hydrology +"""
        self._time_row_index_from_df = (
            self._data_file.index[self._data_file.iloc[:, 0] == "Time (hours)"][0] + 1
        )
        self._time_row_index_from_csv = self._time_row_index_from_df + 2
        return pd.read_csv(self._filepath, skiprows=self._time_row_index_from_df, index_col=0)

    def _get_event(
        self,
        event: str | None = None,
        return_period: float | None = None,
        storm_duration: float | None = None,
        scenario: str | None = None,
    ) -> str:
        """Get exact column name based on event or individual params"""
        if event:
            return next(col for col in self.data.columns if col.lower().startswith(event.lower()))

        if not (return_period and storm_duration and scenario):
            msg = (
                "Missing required inputs to find event, if no event string is passed then a "
                "return_period, storm_duration and scenario are needed. You provided: "
                f"{return_period=}, {storm_duration=}, {scenario=}"
            )
            raise ValueError(msg)
        for column in self.data.columns:
            s, sd, rp, *_ = column.split(" - ")
            if s == scenario and float(sd) == storm_duration and float(rp) == return_period:
                return column
        msg = (
            "No matching event was found based on "
            f"{return_period=}, {storm_duration=}, {scenario=}"
        )
        raise ValueError(msg)

    def get_event_flow(
        self,
        event: str | None = None,
        return_period: float | None = None,
        storm_duration: float | None = None,
        scenario: str | None = None,
    ) -> pd.Series:
        """Extracts a specific event's flow data from the exported Hydrology+ flow data.

        Args:
            event (str, optional): Full string identifier for the event in the dataset. If provided, this takes precedence over other parameters.
            return_period (float, optional): The return period of the event.
            storm_duration (float, optional): The duration of the storm event in hours.
            scenario (str, optional): The scenario name, which typically relates to different conditions (e.g., climate change scenario).

        Returns:
            pd.Series: A pandas Series containing the flow data (m³/s) for the specified event.

        Raises:
            FloodModellerAPIError: If the csv file is not in the correct format.
            ValueError: If the `event` arg is not provided and one or more of `return_period`, `storm_duration`, or `scenario` is missing.
            ValueError: If no matching event is found in the dataset.

        Note:
            - If the `event` parameter is provided, the method returns the data corresponding to that event.
            - If `event` is not provided, the method attempts to locate the event based on the combination of `return_period`, `storm_duration`, and `scenario`.
            - The dataset is assumed to have columns named in the format "scenario - storm_duration - return_period - Flow (m3/s)".
        """

        column = self._get_event(event, return_period, storm_duration, scenario)
        return self.data.loc[:, column]

    def _get_unique_event_components(self):
        return_periods, storm_durations, scenarios = set(), set(), set()
        for column in self.data.columns:
            s, sd, rp, *_ = column.split(" - ")
            return_periods.add(float(rp))
            storm_durations.add(float(sd))
            scenarios.add(s)
        self._return_periods = sorted(return_periods)
        self._storm_durations = sorted(storm_durations)
        self._scenarios = sorted(scenarios)

    @property
    def data(self) -> pd.DataFrame:
        "Hydrograph flow data for all events as a pandas DataFrame."
        return self._data

    @property
    def metadata(self) -> dict[str, str]:
        "Metadata associated with Hydrology+ csv export."
        return self._metadata

    @property
    def return_periods(self) -> list:
        "Distinct return periods from exported Hydrology+ data"
        return self._return_periods

    @property
    def storm_durations(self) -> list:
        "Distinct storm durations from exported Hydrology+ data"
        return self._storm_durations

    @property
    def scenarios(self) -> list:
        "Distinct scenarios from exported Hydrology+ data"
        return self._scenarios

    def _get_output_ief_path(self, event: str) -> Path:
        column_output_name = event.replace("- Flow (m3/s)", "").replace(" ", "")
        return self._filepath.with_name(f"{column_output_name}_generated.ief")

    def generate_iefs(
        self,
        node_label: str,
        template_ief: IEF | Path | str | None = None,
    ) -> list[IEF]:
        """Generates a set of IEF files for all available events in the Hydrology+ Export file.

        The IEF files are saved to disk in the same location as the Hydrology+ Export file and are
        named with the pattern {profile name}_generated.ief. They are also returned as a list of IEF
        instances for further editing/saving if desired.

        Args:
            node_label (str): Node label in model network to associate flow data with.
            template_ief (IEF | Path | str | None, optional): A template IEF instance, a file path, or
                a string representing the path to an IEF. If not provided, a new blank IEF instance is created.

        Returns:
            list[IEF]: A list of IEF instances, one for each event.
        """
        if template_ief is None:
            template_ief = IEF()

        elif isinstance(template_ief, (Path, str)):
            template_ief = IEF(template_ief)

        return [
            self.generate_ief(node_label, template_ief, event=column)
            for column in self.data.columns
        ]

    def generate_ief(  # noqa: PLR0913
        self,
        node_label: str,
        template_ief: IEF | Path | str | None = None,
        event: str | None = None,
        return_period: float | None = None,
        storm_duration: float | None = None,
        scenario: str | None = None,
    ) -> IEF:
        """Generates a single IEF file for the requested event.

        The IEF file is saved to disk in the same location as the Hydrology+ Export file and is
        named with the pattern {profile name}_generated.ief. The IEF instance is also returned for
        further editing/saving if desired.

        Args:
            node_label (str): Node label in model network to associate flow data with.
            template_ief (IEF | Path | str | None, optional): A template IEF instance, a file path, or
                a string representing the path to an IEF. If not provided, a new blank IEF instance is created.
            event (str, optional): Full string identifier for the event in the dataset. If provided, this takes precedence over other parameters.
            return_period (float, optional): The return period of the event.
            storm_duration (float, optional): The duration of the storm event in hours.
            scenario (str, optional): The scenario name, which typically relates to different conditions (e.g., climate change scenario).

        Returns:
            IEF: An IEF instance.
        """
        _template_ief: IEF
        if template_ief is None:
            _template_ief = IEF()

        elif isinstance(template_ief, (Path, str)):
            _template_ief = IEF(template_ief)

        else:
            _template_ief = template_ief

        flowtimeprofile = self.get_flowtimeprofile(
            node_label,
            event,
            return_period,
            storm_duration,
            scenario,
        )
        _template_ief.flowtimeprofiles.append(flowtimeprofile)
        output_ief_path = self._get_output_ief_path(flowtimeprofile.profile)
        _template_ief.save(output_ief_path)
        generated_ief = IEF(output_ief_path)
        _template_ief.flowtimeprofiles = _template_ief.flowtimeprofiles[:-1]

        return generated_ief

    def get_flowtimeprofile(
        self,
        node_label: str,
        event: str | None = None,
        return_period: float | None = None,
        storm_duration: float | None = None,
        scenario: str | None = None,
    ) -> FlowTimeProfile:
        """Generates a FlowTimeProfile object based on the requested event.

        Args:
            node_label (str): Node label in model network to associate flow data with.
            event (str, optional): Full string identifier for the event in the dataset. If provided, this takes precedence over other parameters.
            return_period (float, optional): The return period of the event.
            storm_duration (float, optional): The duration of the storm event in hours.
            scenario (str, optional): The scenario name, which typically relates to different conditions (e.g., climate change scenario).

        Returns:
            FlowTimeProfile: A FlowTimeProfile object containing the attributes required for an IEF.

        Raises:
            FloodModellerAPIError: If the csv file is not in the correct format.
            ValueError: If the `event` arg is not provided and one or more of `return_period`, `storm_duration`, or `scenario` is missing.
            ValueError: If no matching event is found in the dataset.

        Note:
            - If the `event` parameter is provided, the method returns the data corresponding to that event.
            - If `event` is not provided, the method attempts to locate the event based on the combination of `return_period`, `storm_duration`, and `scenario`.
            - The dataset is assumed to have columns named in the format "scenario - storm_duration - return_period - Flow (m3/s)".
        """
        column = self._get_event(event, return_period, storm_duration, scenario)
        index = list(self.data.columns).index(column)
        return FlowTimeProfile(
            labels=[node_label],
            columns=[index + 2],
            start_row=self._time_row_index_from_csv,
            csv_filepath=self._filepath.name,
            file_type="hplus",
            profile=column,
            comment="Generated by HydrologyPlusExport",
        )

    def get_qtbdy(
        self,
        qtbdy_name: str | None,
        event: str | None = None,
        return_period: float | None = None,
        storm_duration: float | None = None,
        scenario: str | None = None,
        **kwargs,
    ) -> QTBDY:
        """Generates a QTBDY unit based on the flow time series of the requested event.

        Args:
            qtbdy_name (str, optional): Name of the new QTBDY unit. If not provided a default name is used.
            event (str, optional): Full string identifier for the event in the dataset. If provided, this takes precedence over other parameters.
            return_period (float, optional): The return period of the event.
            storm_duration (float, optional): The duration of the storm event in hours.
            scenario (str, optional): The scenario name, which typically relates to different conditions (e.g., climate change scenario).
            **kwargs: Additional keyword args can be passed to build the QTBDY unit. See :class:`~floodmodeller_api.units.QTBDY` for details.

        Returns:
            QTBDY: A QTBDY object containing the flow data (m³/s) for the specified event.

        Raises:
            FloodModellerAPIError: If the csv file is not in the correct format.
            ValueError: If the `event` arg is not provided and one or more of `return_period`, `storm_duration`, or `scenario` is missing.
            ValueError: If no matching event is found in the dataset.

        Note:
            - If the `event` parameter is provided, the method returns the data corresponding to that event.
            - If `event` is not provided, the method attempts to locate the event based on the combination of `return_period`, `storm_duration`, and `scenario`.
            - The dataset is assumed to have columns named in the format "scenario - storm_duration - return_period - Flow (m3/s)".
        """
        flow_data = self.get_event_flow(event, return_period, storm_duration, scenario)
        return QTBDY(name=qtbdy_name, data=flow_data, **kwargs)
