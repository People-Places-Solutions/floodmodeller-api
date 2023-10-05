""" This sample script demonstrates simple way to produce an interactive chart using the plotly
    package based on a ZZN file """

# Import modules
import os
import sys
from pathlib import Path

try:
    import plotly.graph_objects as go
except ImportError:
    print("Importing plotly package failed, this script requires you to have plotly installed")
    sys.exit()
try:
    from floodmodeller_api import ZZN
except ImportError:
    print(
        "Import failed - Please ensure you have correctly installed floodmodeller_api to your active environment"
    )
    sys.exit()

script_loc = Path(__file__).resolve().parent
os.chdir(script_loc)  # Set current working directory to this script location

zzn_file = Path("sample_data\\EX3.zzn")

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
