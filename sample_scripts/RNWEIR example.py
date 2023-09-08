# Import modules
import sys
import os
from pathlib import Path

try:
    from floodmodeller_api import DAT
except ImportError:
    print(
        "Import failed - Please ensure you have correctly installed floodmodeller_api to your active environment"
    )
    sys.exit()

script_loc = Path(__file__).resolve().parent
os.chdir(script_loc)  # Set current working directory to this script location

# Initialise DAT class
dat = DAT("sample_data/ex4.DAT")

# Iterate through all round nosed weir sections
for name, structure in dat.structures.items():
    if structure._unit == "RNWEIR":
        structure.upstream_crest_height += 0.3  # Increase upstream crest height by 0.3m

dat.save("sample_data/ex4_changed.DAT")
