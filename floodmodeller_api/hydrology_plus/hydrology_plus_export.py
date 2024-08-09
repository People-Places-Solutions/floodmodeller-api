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

from pathlib import Path

import pandas as pd

from floodmodeller_api._base import FMFile
from floodmodeller_api.util import handle_exception


class HydrologyPlusExport(FMFile):
    """Class to handle the output of Hydrology +

    Args:
        csv file (str): produced by Hydrology + in Flood Modeller

    Output:
        Initiates 'HydrologyPlusExport' object
        The event/s needed to run simulations in Flood Modeller
    """

    _filetype: str = "HydrologyPlusExport"
    _suffix: str = ".csv"

    @handle_exception(when="read")
    def __init__(self, csv_file_path: Path, from_json: bool = False):
        if from_json:
            return
        FMFile.__init__(self, csv_file_path)
        self._read()

    def _read(self):
        self._data_file = pd.read_csv(self._filepath)
        self.metadata = self._get_metadata()
        self.data = self._get_df_hydrographs_plus()

    def _get_metadata(self) -> dict[str, str]:
        """Extracts the metada from the hydrology + results"""
        metadata_row_index = self._data_file.index[self._data_file.iloc[:, 0] == "Return Period"][0]
        metadata_df = self._data_file.iloc[:metadata_row_index, 0].tolist()

        return dict([row.split("=") for row in metadata_df])

    def _get_df_hydrographs_plus(self) -> pd.DataFrame:
        """Extracts all the events generated in hydrology +"""
        time_row_index = self._data_file.index[self._data_file.iloc[:, 0] == "Time (hours)"][0]
        col_names = self._data_file.iloc[time_row_index]
        new_col_names = list(col_names)
        df_events = self._data_file.iloc[time_row_index + 1 :].reset_index(drop=True)
        df_events.columns = new_col_names
        for col in df_events.columns[:]:
            df_events[col] = pd.to_numeric(df_events[col], errors="coerce")

        return df_events.set_index("Time (hours)")

    def get_event(self, event: str) -> pd.Series:
        """Extracts a particular event to be simulated in Flood Modeller"""

        return self.data.loc[:, f"{event} - Flow (m3/s)"]


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
    event_plus = baseline_unchecked.get_event(event)
    print(event_plus)
    print("################################################")
