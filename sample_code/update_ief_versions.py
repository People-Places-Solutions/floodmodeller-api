""" This sample script shows how a single IEF can be simulated directly using python """

# Import modules
import os
import sys
from glob import glob
from pathlib import Path

try:
    from floodmodeller_api import IEF
except ImportError:
    print(
        "Import failed - Please ensure you have correctly installed floodmodeller_api to your active environment",
    )
    sys.exit()

script_loc = Path(__file__).resolve().parent
os.chdir(script_loc)  # Set current working directory to this script location

# Get list of IEF files using glob function
ief_files = glob("sample_data/*.ief")

for ief_path in ief_files:
    ief_name = os.path.basename(ief_path)  # get existing filename
    new_ief_name = ief_name.replace(".ief", "_v2.ief")  # update filename with 'v2' appended
    new_ief_path = Path("sample_data", new_ief_name)  # get updated filepath

    ief = IEF(ief_path)  # Initiate IEF Class Object
    ief.Title += "_v2"  # Update title
    if "Results" in dir(ief):
        ief.Results += "_v2"  # If Results setting already exists, append v2
    else:
        ief.Results = "v2"  # If no results yet specified, set results to v2

    ief.save(new_ief_path)  # Save updated IEF files to the new filepath
