import csv
import os
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from floodmodeller_api import ZZN


def run():
    # Manually link an event to a model
    # event folder - The name of the folder in which the event data is in. The folder will be used as the name for the event on the plot dropdown.
    # event data - The event/real data (.xlsx file).
    # model results - The model data (.zzn file).
    model_event_links = [
        {
            "event folder": "",
            "event data": ".xlsx",
            "model results": ".zzn",
        },
        {
            "event folder": "",
            "event data": ".xlsx",
            "model results": ".zzn",
        },
        {
            "event folder": "",
            "event data": ".xlsx",
            "model results": ".zzn",
        },
        {
            "event folder": "",
            "event data": ".xlsx",
            "model results": ".zzn",
        },
    ]  # NB: If you want to add more model & event links copy and paste the { ... }, inside the square brackets (array) as many times as you need.
    # Full path to the list of gauge locations and their node names.
    gauge_locations_path = r""
    # Full path to folder which the model files are in.
    models_path = r""
    # Full path to the folder in which the event folders are in.
    event_data_folder_path = r""
    # Full path to the folder where you want to put your output data into.
    output_folder = r""

    # All data needed has been added you should be able to run the file now.
    c = Calibration()
    c.calibrate_node(
        model_event_links,
        gauge_locations_path,
        models_path,
        event_data_folder_path,
        output_folder,
    )


class Calibration:
    def __init__(self) -> None:
        pass

    def calibrate_node(  # noqa: PLR0913
        self,
        model_event_links,
        gauge_locations_path,
        models_path,
        event_data_path,
        output_folder,
    ):
        self._model_event_links = model_event_links
        print("Linked models to events")
        self._read_nodes(gauge_locations_path)
        print("Read in node names")
        self._set_zzn_stage(models_path)
        print("Read in zzn files")
        model_data_list = self._model_data()
        print("Cleaned model data")
        event_data = self._event_data(event_data_path)
        print("Read in + cleaned event data")
        combined = self._combine_df(event_data, model_data_list)
        print("Combined all data")
        self._output_data(combined, output_folder)
        print("Finished")

    def _read_nodes(self, gauge_locations_path):
        gauges_nodes = pd.read_excel(gauge_locations_path)
        tabs = list(gauges_nodes["Tab"])
        nodes = list(gauges_nodes["Node"])

        self._node_dict = {}
        for i in range(0, len(nodes)):
            self._node_dict[nodes[i]] = tabs[i]

        self._nodes = list(self._node_dict.keys())

    def _set_zzn_stage(self, models_path):
        self._model_names = []
        self._model_dfs = []
        for link in self._model_event_links:
            file = link["model results"]
            zzn = ZZN(Path(models_path, file))
            df = zzn.to_dataframe(variable="Stage")
            self._model_names.append(file[:-4])
            self._model_dfs.append(df)

    def _model_data(self):
        model_data_list = []
        node_name_list = []
        for i, model_df in enumerate(self._model_dfs):
            model_nodes_list = []
            name_list = []
            for node in self._nodes:
                if node in model_df:
                    model_nodes_list.append(model_df[node])
                    name_list.append(f"{node}_{self._model_names[i]}")
            node_name_list.append(name_list)
            model_nodes_df = pd.concat(model_nodes_list, axis=1)
            model_data_list.append(model_nodes_df)
        return [model_data_list, node_name_list]

    def _event_data(self, event_data_path):
        xlsx_file_paths = []
        self._event_names = []
        for link in self._model_event_links:
            folder = link["event folder"]
            file = link["event data"]
            file_path = str(Path(event_data_path, folder, file))
            xlsx_file_paths.append(file_path)
            self._event_names.append(folder)

        print("Found event data path")

        event_data_list = []
        index = 1
        for i, event in enumerate(self._event_names):
            for node in self._nodes:
                try:
                    sheet = pd.read_excel(xlsx_file_paths[i], sheet_name=self._node_dict[node])
                    time = list(filter(lambda x: x is not None, (list(sheet.iloc[:, 0])[13:])))
                    values = list(filter(lambda x: x is not None, (list(sheet.iloc[:, 2])[13:])))
                    event_data_list.append(
                        pd.DataFrame(
                            {f"{node}_{event}": values},
                            index=pd.Index(time, name="Time (hr)"),
                        )
                    )
                    print(
                        f"Added {self._node_dict[node]} for {event}: {index}/{len(self._event_names) * len(self._nodes)}"
                    )
                except Exception:
                    print(
                        f"Failed to add {self._node_dict[node]} for {event}: {index}/{len(self._event_names) * len(self._nodes)}"
                    )
                index += 1
                # workbook file can't be found, or node sheet can't be found
        return event_data_list

    def _combine_df(self, event_data, model_data):
        model_data_dfs = model_data[0]
        model_data_cols = model_data[1]
        for i, df in enumerate(model_data_dfs):
            df.columns = model_data_cols[i]

        model_df = pd.concat(model_data_dfs, axis=1)
        event_df = pd.concat(event_data, axis=1)

        # make them the dataframes the same length
        num_model_rows = len(model_df)
        num_event_rows = len(event_df)
        if num_model_rows != num_event_rows:
            if num_model_rows < num_event_rows:
                num_rows = num_model_rows
                event_df = event_df.head(num_rows)
            else:
                num_rows = num_event_rows
                model_df = model_df.head(num_rows)

        return [model_df, event_df]

    def _output_data(self, combined_data, output_folder):
        model_df = combined_data[0]
        event_df = combined_data[1]
        csv_list = [
            [
                "Gauge",
                "Event",
                "Model Peak",
                "Event Peak",
                "Peak Difference",
                "Model Peak Time",
                "Event Peak Time",
                "Peak Time Difference",
            ],
        ]

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        self._starting_y_coords = None
        node_dropdown = []

        for node in self._nodes:
            filtered_dfs = self._filter_by_node(model_df, event_df, node)
            node_filtered_model = filtered_dfs[0]
            node_filtered_event = filtered_dfs[1]

            if len(node_filtered_model.columns) == 0 or len(node_filtered_event.columns) == 0:
                continue

            self._add_node_dropdown(node, node_filtered_model, node_filtered_event, node_dropdown)

            self._fill_csv_list(
                node,
                node_filtered_model,
                node_filtered_event,
                csv_list,
            )

        setup = self._setup_plot(model_df.index)
        fig = setup[0]
        trace_events = setup[1]

        self._create_html(fig, node_dropdown, trace_events, output_folder)
        print("Plotted data")
        self._outputs_csv(csv_list, output_folder)
        print("Filled out csv data")
        self._dump_df(model_df, event_df, output_folder)
        print("Dumped dataframe to csv")

    def _filter_by_node(self, model_df, event_df, node):
        node_model_mask = [col for col in model_df.columns if node in col]
        node_filtered_model = model_df[node_model_mask]
        node_event_mask = [col for col in event_df.columns if node in col]
        node_filtered_event = event_df[node_event_mask]

        return [node_filtered_model, node_filtered_event]

    def _setup_plot(self, index):
        fig = go.Figure()

        model_y_coords = self._starting_y_coords[0]
        event_y_coords = self._starting_y_coords[1]

        # Add a model and event line for all events
        trace_events = []
        show = True
        for count, event in enumerate(self._event_names):
            if count > 0:
                show = False
            if count < len(model_y_coords):
                fig.add_trace(
                    go.Scatter(
                        x=index,
                        y=model_y_coords[count],
                        visible=show,
                        name="Model Data",
                        mode="lines",
                    )
                )
                trace_events.append(event)
            if count < len(event_y_coords):
                fig.add_trace(
                    go.Scatter(
                        x=index,
                        y=event_y_coords[count],
                        visible=show,
                        name="Event Data",
                        mode="lines",
                    )
                )
            trace_events.append(event)

        return [fig, trace_events]

    def _add_node_dropdown(self, node, node_filtered_model, node_filtered_event, dropdown_buttons):
        y_coords = []
        y_model = []
        y_event = []
        for column in node_filtered_model.columns:
            model = list(node_filtered_model[column])
            y_coords.append(model)
            if self._starting_y_coords is None:
                y_model.append(model)
        for column in node_filtered_event.columns:
            event = list(node_filtered_event[column])
            y_coords.append(event)
            if self._starting_y_coords is None:
                y_event.append(event)
        if self._starting_y_coords is None:
            self._starting_y_coords = [y_model, y_event]

        dropdown_buttons.append(
            {
                "method": "update",
                "label": self._node_dict[node],
                "visible": True,
                "args": [{"y": y_coords}],
            }
        )

    def _create_html(self, fig, nodes_dropdown, trace_events, output_folder):
        events_dropdown = []
        for event in self._event_names:
            show_event = [event in x for x in trace_events]
            events_dropdown.append(
                {
                    "method": "update",
                    "label": f"{event}",
                    "visible": True,
                    "args": [{"visible": show_event}],
                }
            )

        # dropdown
        fig.update_layout(
            updatemenus=[
                {
                    "buttons": nodes_dropdown,
                    "direction": "down",
                    "name": "Node",
                    "x": -0.05,
                    "y": 1.1,
                },
                {
                    "buttons": events_dropdown,
                    "direction": "down",
                    "name": "Event",
                    "x": -0.05,
                    "y": 1.0,
                },
            ]
        )

        fig.update_layout(
            title={"text": "Model Calibration", "y": 0.95, "x": 0.5},
            xaxis_title="Time from start (hrs)",
            yaxis_title="Water level (m)",
        )

        fig.write_html(Path(output_folder, "Calibration.html"))

    def _fill_csv_list(self, node, node_filtered_model, node_filtered_event, csv_list):
        for link in self._model_event_links:
            model_col_name = f"{node}_{link['model results']}"[:-4]
            event_col_name = f"{node}_{link['event folder']}"
            if (
                model_col_name in node_filtered_model.columns
                and event_col_name in node_filtered_event.columns
            ):
                model_col = (node_filtered_model[f"{node}_{link['model results']}"[:-4]]).replace(
                    "---", np.nan
                )
                event_col = (node_filtered_event[f"{node}_{link['event folder']}"]).replace(
                    "---", np.nan
                )
                model_peak = model_col.max()
                event_peak = event_col.max()
                model_time_peak = model_col.idxmax()
                event_time_peak = event_col.idxmax()
                csv_list.append(
                    [
                        self._node_dict[node],
                        link["event folder"],
                        model_peak,
                        event_peak,
                        f"{abs(model_peak - event_peak):.3f}",
                        model_time_peak,
                        event_time_peak,
                        f"{abs(model_time_peak - event_time_peak):.3f}",
                    ]
                )

    def _outputs_csv(self, csv_list, output_folder):
        with open(Path(output_folder, "Gauge_Peak_Data.csv"), "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            for line in csv_list:
                writer.writerow(line)

    def _dump_df(self, model_df, event_df, output_folder):
        combined = model_df.join(event_df)
        combined.to_excel(Path(output_folder, "Full_Dataframe.xlsx"), index=True)


run()
