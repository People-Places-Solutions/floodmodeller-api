""" This sample script demonstrates a process to automatically adjust all QTBDY units in an IED file
    to maintain a minimum flow of 50% of the peak throughout the falling limb. """

# Import modules
import sys
import os
from pathlib import Path

try:
    from floodmodeller_api import IED
    from floodmodeller_api.units import (
        QTBDY,
    )  # importing the QTBDY Unit class to enable checking unit type
except ImportError:
    print(
        "Import failed - Please ensure you have correctly installed floodmodeller_api to your active environment"
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
        if time > peak_flow_idx:  # For only flows after peak flow i.e. falling limb
            if flow < peak_flow * 0.5:  # If the flow is less than 50% of the peak
                hydrograph.loc[time] = (
                    peak_flow * 0.5
                )  # Maintain minimum flow of 50% of peak for remainder of hydrograph


# Iterate through all QTBDY units
for name, unit in ied.boundaries.items():
    if type(unit) == QTBDY:  # check if unit is a QTBDY type
        update_hydrograph(unit)  # Call the custom function defined above to alter hydrograph

ied.save("sample_data\\EX3_qt_adjusted.IED")  # Update the changes in the IED file
