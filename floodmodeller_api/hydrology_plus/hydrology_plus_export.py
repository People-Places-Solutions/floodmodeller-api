"""
Flood Modeller Python API
Copyright (C) 2024 Jacobs U.K. Limited

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see https://www.gnu.org/licenses/.

If you have any query about this program or this License, please contact us at support@floodmodeller.com or write to the following
address: Jacobs UK Limited, Flood Modeller, Cottons Centre, Cottons Lane, London, SE1 2QG, United Kingdom.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

from floodmodeller_api._base import FMFile
from floodmodeller_api.util import handle_exception

if TYPE_CHECKING:
    from pathlib import Path


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
                raise ValueError("Input file is not the correct format for Hydrology+ export data.")

        self._data_file = pd.read_csv(self._filepath)
        self._metadata = self._get_metadata()
        self._data = self._get_df_hydrographs_plus()
        self._get_unique_event_components()

    def _get_metadata(self) -> dict[str, str]:
        """Extracts the metada from the hydrology + results"""
        metadata_row_index = self._data_file.index[self._data_file.iloc[:, 0] == "Return Period"][0]
        metadata_df = self._data_file.iloc[:metadata_row_index, 0].tolist()

        return dict([row.split("=") for row in metadata_df])

    def _get_df_hydrographs_plus(self) -> pd.DataFrame:
        """Extracts all the events generated in hydrology +"""
        time_row_index = self._data_file.index[self._data_file.iloc[:, 0] == "Time (hours)"][0]
        return pd.read_csv(self._filepath, skiprows=time_row_index + 1, index_col=0)

    def get_event(
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
            FloodModellerAPIError: If the `event` arg is not provided and one or more of `return_period`, `storm_duration`, or `scenario` is missing.
            FloodModellerAPIError: If no matching event is found in the dataset.

        Note:
            - If the `event` parameter is provided, the method returns the data corresponding to that event.
            - If `event` is not provided, the method attempts to locate the event based on the combination of `return_period`, `storm_duration`, and `scenario`.
            - The dataset is assumed to have columns named in the format "scenario - storm_duration - return_period - Flow (m3/s)".
        """
        if event:
            column = next(col for col in self.data.columns if col.lower().startswith(event.lower()))
            return self.data.loc[:, column]
        if not (return_period and storm_duration and scenario):
            raise ValueError(
                "Missing required inputs to find event, if no event string is passed then a "
                "return_period, storm_duration and scenario are needed. You provided: "
                f"{return_period=}, {storm_duration=}, {scenario=}",
            )
        for column in self.data.columns:
            s, sd, rp, *_ = column.split(" - ")
            if s == scenario and float(sd) == storm_duration and float(rp) == return_period:
                return self.data.loc[:, column]
        else:
            raise ValueError(
                "No matching event was found based on "
                f"{return_period=}, {storm_duration=}, {scenario=}",
            )

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


if __name__ == "__main__":
    event = "2020 Upper - 11 - 1"
    baseline_unchecked = HydrologyPlusExport(
        r"..\floodmodeller-api\floodmodeller_api\test\test_data\Baseline_unchecked.csv",
    )
    print("################################################")
    print(baseline_unchecked.metadata)
    print("################################################")
    print(baseline_unchecked.data)
    print("################################################")
    event_plus = baseline_unchecked.get_event(
        scenario="2020 Upper",
        storm_duration=11.0,
        return_period=1,
    )
    print(event_plus)
    print("################################################")
    print(list(HydrologyPlusExport(r"..\floodmodeller-api\floodmodeller_api\test\test_data\Baseline_unchecked.csv").data))