import plotly.graph_objects as go
import pandas as pd
from floodmodeller_api import ZZN
import os

from dash import Dash, dcc, html, Input, Output
import webbrowser
from threading import Thread
import time
import keyboard


def test():
    gauge_locations_path = r""
    node = "B16800"  # Acle Bridge
    variable = "Stage"
    model_zzn_path = r"C:\FloodModellerJacobs\Calibration Data\1DResults\BROADLANDS_BECCLES_51_V01_MHWS_0_1PCT_W0_05_1080HRS.zzn"
    event_data_folder_path = r"C:\FloodModellerJacobs\Calibration Data\EventData"
    c = Calibration(gauge_locations_path)
    c.calibrate_node(node, variable, model_zzn_path, event_data_folder_path)


class Calibration:
    def __init__(self, gauge_locations_path) -> None:
        # in the nodes one if the node isnt in the data frame dont add it from the csv file
        self._set_nodes()  # add gauge locations path input
        self._set_node_dict()  # + stick in a method together

    def calibrate_node(self, node, variable, zzn_path, event_data_path):
        self._set_zzn_stage(zzn_path, variable)
        model_data = self._model_data(node)
        real_data = self._event_data(node, event_data_path)
        combined = self._combine_df(real_data, model_data)
        self._plot(node, combined)

    def _model_data(self, node):
        model_data = self._stage_df[node].to_frame()
        model_data.rename(columns={node: "Model Data"}, inplace=True)
        return model_data

    def _event_data(self, node, event_data_path):
        xlsx_file_paths = []
        line_names = []

        folders = os.listdir(event_data_path)
        for folder in folders:
            folder_path = event_data_path + r"\\" + folder
            files = os.listdir(folder_path)
            for file in files:
                if "Levels" in file:
                    file_path = folder_path + r"\\" + file
                    xlsx_file_paths.append(file_path)
                    line_names.append(folder)

        real_data_list = []
        index = 0
        for file_path in xlsx_file_paths:
            sheet = pd.read_excel(file_path, sheet_name=self._node_dict[node])
            time = list(filter(lambda x: x is not None, (list(sheet.iloc[:, 0])[13:])))
            values = list(filter(lambda x: x is not None, (list(sheet.iloc[:, 2])[13:])))
            file_path.split()
            real_data_list.append(pd.DataFrame(
                {line_names[index]: values},
                index=pd.Index(time, name="Time (hr)"),
            ))
            index += 1
        real_data = pd.concat(real_data_list,axis=1)
        self._line_names = line_names
        return real_data

    def _combine_df(self, real_data, model_data):
        combined = model_data.join(real_data, how="right")
        self._line_names.append("Model Data")
        return combined

    def _plot(self, node, combined_data):
        name = self._node_dict[node]
        fig = go.Figure()
        for column in self._line_names:
            fig.add_trace(go.Scatter(x=combined_data.index, y=combined_data[column], name=column, mode="lines"))

        buttons = self._line_names
        #for col in df.columns:
        #    buttons.append(
        #        dict(
        #            method='restyle',
        #            label=col,
        #            visible=True,
        #            args=[{'y':[df[col]]}],
        #        )
        #    )

        fig.update_layout(
            title={
                'text' : f"{name} - {node}",
                'y' : 0.95,
                'x' : 0.5
                },
            xaxis_title="Time from start (hrs)",
            yaxis_title="Water level (m)",
            #updatemenus = [
            #    dict(
            #        buttons = buttons,
            #        direction = 'down',
            #        name = 'Node'
            #    )]
        )

        fig.write_html(r"C:\FloodModellerJacobs\Calibration Data\html\test.html")#Path(zzn_file.parent, f'{zzn_file.stem}_interactive_flow.html'))

        # !!!for old plotly.express!!!
        #fig = px.line(
        #    combined_data,
        #    x=combined_data.index,
        #    y=self._line_names,
        #    title=f"{name} - {node}",
        #).update_layout(
        #    xaxis_title="Time from start (hr)",
        #    yaxis_title="Water Level (m)",
        #)
        ##fig.for_each_trace(None)
        #fig.show()

    def _set_nodes(self):
        self._nodes = [
            "B16800",
            "A7316U",
            "W28757",
            "W28757",
            "Y200",
            "Y4900M",
            "Y22800",
            "B200M",
            "W1200",
            "W17800",
            "Y13800",
            "WE1227d",
            "Y0M",
            "W9000U",
            "Y770D",
            "CD35RU",
            "BA19113",
            "WENF1_0d",
            "WENF1_0u",
            "OD3580",
            "BA9511",
            "Y7600",
            "T3600",
            "HB_0269",
            "B2800U",
            "YARE00988",
            "A12206d",
        ]

    def _set_node_dict(self):
        self._node_dict = {
            "B16800": "Acle Bridge",
            "A7316U": "Barton Broad",
            "W28757": "Beccles Quay (Bridge)",
            "W28757": "Beccles Quay (Tide)",
            "Y200": "Berney Arms",
            "Y4900M": "Breydon Bridge",
            "Y22800": "Brundall",
            "B200M": "Bure Bridge",
            "W1200": "Burgh Castle",
            "W17800": "Burgh St Peter",
            "Y13800": "Cantley",
            "WE1227d": "Carrow Bridge",
            "Y0M": "Great Yarmouth T.S.",
            "W9000U": "Haddiscoe",
            "Y770D": "Haven Bridge",
            "CD35RU": "Hickling Broad",
            "BA19113": "Hoveton Broad",
            "WENF1_0d": "New Mills Norwich Sluice (downstream)",
            "WENF1_0u": "New Mills Norwich Sluice (upstream)",
            "OD3580": "Oulton Broad",
            "BA9511": "Ranworth Broad",
            "Y7600": "Reedham",
            "T3600": "Repps",
            "HB_0269": "Rockland St Mary",
            "B2800U": "Three Mile House",
            "YARE00988": "Trowse (upstream)",
            "A12206d": "Wayford Bridge",
        }

    def _set_zzn_stage(self, zzn_path, variable):
        z = ZZN(zzn_path)
        df = z.to_dataframe(variable=variable)
        self._stage_df = df




test()
