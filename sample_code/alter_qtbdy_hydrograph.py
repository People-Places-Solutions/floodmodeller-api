"""This sample script demonstrates a process to automatically adjust all QTBDY units in an IED file
to maintain a minimum flow of 50% of the peak throughout the falling limb."""

# Import modules
import os
import sys
from pathlib import Path

try:
    from floodmodeller_api import IED
    from floodmodeller_api.units import QTBDY  # to enable checking unit type
except ImportError:
    print(
        "Import failed - Please ensure you have correctly installed floodmodeller_api to your active environment",
    )
    sys.exit()

script_loc = Path(__file__).resolve().parent
os.chdir(script_loc)  # Set current working directory to this script location

# Read IED file into new IED Class object
ied = IED("sample_data\\EX3.IED")


# Define custom function to alter the flow hydrograph to have a minimum flow of 30% of peak flow ONLY on the falling limb
def update_hydrograph(qtbdy_unit):
    hydrograph = qtbdy_unit.data  # Get hydrograph from qtbdy unit
    peak_flow = hydrograph.max()  # Get peak flow value
    peak_flow_idx = hydrograph.loc[hydrograph == peak_flow].index  # Get index of peak flow
    for time, flow in hydrograph.items():  # Iterate through hydrograph series
        # For only flows after peak flow i.e. falling limb
        # If the flow is less than 50% of the peak
        if (time > peak_flow_idx) and (flow < peak_flow * 0.5):
            # Maintain minimum flow of 50% of peak for remainder of hydrograph
            hydrograph.loc[time] = peak_flow * 0.5


# Iterate through all QTBDY units
for unit in ied.boundaries.values():
    if isinstance(unit, QTBDY):  # check if unit is a QTBDY type
        update_hydrograph(unit)  # Call the custom function defined above to alter hydrograph

ied.save("sample_data\\EX3_qt_adjusted.IED")  # Update the changes in the IED file
