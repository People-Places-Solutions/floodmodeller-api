""" This sample script shows how to extract max results from a zzn file into a pandas dataframe """

# Import modules
import sys
import os
from pathlib import Path

try:
    from floodmodeller_api import ZZN
except ImportError:
    print(
        "Import failed - Please ensure you have correctly installed floodmodeller_api to your active environment"
    )
    sys.exit()

script_loc = Path(__file__).resolve().parent
os.chdir(script_loc)  # Set current working directory to this script location

# Initialise ZZN class
zzn = ZZN("sample_data/ex3.zzn")

# Export results to dataframe
results_df = zzn.to_dataframe(result_type="max")

print(results_df)  # print dataframe to console
