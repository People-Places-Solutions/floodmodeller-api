""" This sample script demonstrates simple way to produce an interactive chart using the plotly 
    package based on a ZZN file """

# Import modules
import sys
import os
from pathlib import Path
import plotly.graph_objects as go
from floodmodeller_api import ZZN


zzn_file = Path(
    r"C:\Users\MW055122\Data Science\floodmodeller-api\sample_scripts\sample_data\EX3.zzn"
)


def flow_graph(zzn_file: Path):
    # Read ZZN file
    zzn = ZZN(zzn_file)
    df = zzn.to_dataframe(variable="Flow")  # Output dataframe of flows

    fig = go.Figure()  # Create new plotly figure

    # Add line scatter to chart based on first section
    fig.add_scatter(
        x=df.index,
        y=df[df.columns[0]],
        mode="lines",
    )

    # Create a button for each section that updates the chart to show that
    # section's flow data
    buttons = []
    for col in df.columns:
        buttons.append(
            dict(
                method="restyle",
                label=col,
                visible=True,
                args=[{"y": [df[col]]}],
            )
        )

    # Update the chart layout with labels and add a dropdown menu with all buttons
    fig.update_layout(
        title={"text": "Modelled Flow", "y": 0.95, "x": 0.5},
        xaxis_title="Time (hrs)",
        yaxis_title="Flow (m3/s)",
        updatemenus=[dict(buttons=buttons, direction="down", name="Node")],
    )

    # Save chart to HTML file
    fig.write_html(Path(zzn_file.parent, f"{zzn_file.stem}_interactive_flow.html"))


from floodmodeller_api.toolbox import FMTool, Parameter


class InteractiveFlow(FMTool):
    name = "Visualise Flow Graph"
    description = "This tool reads a zzn_file and visualises the flow graph"
    parameters = [Parameter("zzn_file", str)]
    tool_function = flow_graph


if __name__ == "__main__":
    tool = InteractiveFlow()
    tool.run_from_command_line()
