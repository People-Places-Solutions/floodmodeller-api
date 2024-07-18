import pandas as pd


class HydrographPlus:
    """Class to hande the output of Hydrology +."""
    def __init__(self, data_file):
        self.data_file = pd.read_csv(data_file, header=None)

    def get_metada(self) -> dict[str, str]:
        metadata_row_index = self.data_file.index[self.data_file.apply(lambda row: row.str.contains("Return Period")).any(axis=1)][0]
        metadata_df = self.data_file.iloc[1:metadata_row_index, 0:1]

        return {row.split("=")[0]: row.split("=")[1] for row in metadata_df.iloc[:, 0]}

    def get_df_hydrographs_plus(self):
        time_row_index = self.data_file.index[self.data_file.apply(lambda row: row.str.contains("Time \(hours\)")).any(axis=1)][0]
        self.columns = self.data_file.iloc[time_row_index]
        df_events = self.data_file.iloc[time_row_index+1:].reset_index(drop=True)
        df_events.columns = self.columns
        for col in df_events.columns[1:]:
            df_events[col] = pd.to_numeric(df_events[col], errors="coerce")

        return df_events

    def get_event(self, df_flows: pd.DataFrame, event: str) -> pd.DataFrame:
        def _remove_string_from_list_items(lst, string) -> list[str]:
            return [item.replace(string, "") for item in lst]

        def _find_index(lst, string) -> int:
            for i, item in enumerate(lst):
                if string in item:
                    return i
            return -1
        index_columns = _remove_string_from_list_items(df_flows.columns, " - Flow (m3/s)")
        index_event = _find_index(index_columns, event)
        column_index = [0, index_event]

        return df_flows.iloc[:, column_index]



if __name__ == "__main__":
    event = "2020 Upper - 11 - 1"
    baseline_unchecked = HydrographPlus(r"C:\Users\caballva\OneDrive - Jacobs\Documents\PROJECTS\FLOOD_MODELLER_API\H+\H+ForFMAPI2\associated_data\Baseline unchecked.csv")
    print("################################################")
    metadata = baseline_unchecked.get_metada()
    print(metadata)
    print("################################################")
    hydrographs = baseline_unchecked.get_df_hydrographs_plus()
    print(hydrographs)
    print("################################################")
    event_plus = baseline_unchecked.get_event(hydrographs, event)
    print(event_plus)
    print("################################################")
