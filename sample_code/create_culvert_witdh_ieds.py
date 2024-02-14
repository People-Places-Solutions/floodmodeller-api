""" This sample script demonstrates how you could create a set of new IED files, each representing a different
    culvert width for the culvert 'T2' """

# Import modules
import os
import sys
from pathlib import Path

try:
    from floodmodeller_api import DAT, IED
except ImportError:
    print(
        "Import failed - Please ensure you have correctly installed floodmodeller_api to your active environment",
    )
    sys.exit()

script_loc = Path(__file__).resolve().parent
os.chdir(script_loc)  # Set current working directory to this script location

dat_file = Path("sample_data\\EX17.DAT")

dat = DAT(dat_file)  # Read DAT file
culvert = dat.conduits["T2"]  # get culvert unit 'T2'

# Loop through each width
for width in [2.5, 2.6, 2.7, 2.8]:
    ied = IED(None)  # Create blank IED file
    culvert.width = width  # Set the width of culvert unit to the desired width
    ied.conduits[culvert.name] = culvert  # Add culvert unit to the blank IED
    ied.save(
        Path(dat_file.parent, f"{dat_file.stem}_{width*1000}mm_width.IED"),
    )  # Save IED with name based on dat file and width
