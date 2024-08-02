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


import pandas as pd

from floodmodeller_api._base import FMFile
from floodmodeller_api.util import handle_exception


class HydrographPlusExport(FMFile):
    """Class to handle the output of Hydrology +.
    Args:
        The csv file produced by Hydrology + in Flood Modeller

    Output:
        Initiates 'HydrographPlus' object
        The event/s needed to run simulations in Flood Modeller
    """

    _filetype: str = "HydrographPlusExport"
    _suffix: str = ".csv"

    @handle_exception(when="read")
    def __init__(self, csv_file_path, from_json: bool = False):
        if from_json:
            return
        FMFile.__init__(self, csv_file_path)
        self._read()

    def _read(self):
        self.data_file = pd.read_csv(self._filepath)
        self.metadata = self._get_metadata()
        self.data_flows = self._get_df_hydrographs_plus()

    def _get_metadata(self) -> dict[str, str]:
        """To extract the metada from the hydrology + results"""
        metadata_row_index = self.data_file.index[
            self.data_file.apply(lambda row: row.str.contains("Return Period")).any(axis=1)
        ][0]
        metadata_df = self.data_file.iloc[:metadata_row_index, 0:1]

        return {row.split("=")[0]: row.split("=")[1] for row in metadata_df.iloc[:, 0]}

    def _get_df_hydrographs_plus(self) -> pd.DataFrame:
        """To extract all the events generated in hydrology +"""
        time_row_index = self.data_file.index[
            self.data_file.apply(lambda row: row.str.contains(r"Time \(hours\)")).any(axis=1)
        ][0]
        col_names = self.data_file.iloc[time_row_index]
        new_col_names = list(col_names)
        df_events = self.data_file.iloc[time_row_index + 1 :].reset_index(drop=True)
        df_events.columns = new_col_names
        for col in df_events.columns[:]:
            df_events[col] = pd.to_numeric(df_events[col], errors="coerce")

        return df_events.set_index("Time (hours)")

    def get_event(self, event: str) -> pd.DataFrame:
        """To extract a particular event to be simulated in Flood Modeller"""

        return self.data_flows.loc[:, f"{event} - Flow (m3/s)"]



if __name__ == "__main__":
    event = "2020 Upper - 11 - 1"
    baseline_unchecked = HydrographPlusExport(
        r"..\floodmodeller-api\floodmodeller_api\test\test_data\Baseline_unchecked.csv",
    )
    print("################################################")
    print(baseline_unchecked.metadata)
    print("################################################")
    print(baseline_unchecked.data_flows)
    print("################################################")
    event_plus = baseline_unchecked.get_event(event)
    print(event_plus)
    print("################################################")
