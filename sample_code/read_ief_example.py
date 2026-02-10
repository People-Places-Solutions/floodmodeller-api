"""This sample script shows how a single IEF can be simulated directly using python"""

# Import modules
import os
import sys
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
ief = IEF(Path("sample_data/ex3.ief"))

pass
