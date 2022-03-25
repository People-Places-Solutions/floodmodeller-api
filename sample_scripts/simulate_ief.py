''' This sample script shows how a single IEF can be simulated directly using python '''

# Import modules
import sys
import os
from pathlib import Path
try:
    from floodmodeller_api import IEF
except ImportError:
    print('Import failed - Please ensure you have correctly installed floodmodeller_api to your active environment')
    sys.exit()

script_loc = Path(__file__).resolve().parent
os.chdir(script_loc) # Set current working directory to this script location

# Initialise ief object
ief = IEF("sample_data\\ex3.ief")

# Execute simulation
ief.simulate()