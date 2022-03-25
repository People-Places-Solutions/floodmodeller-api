''' This sample script shows how to extract the flow time series for a single node from a zzn file '''

# Import modules
import sys
import os
from pathlib import Path
try:
    from floodmodeller_api import ZZN
except ImportError:
    print('Import failed - Please ensure you have correctly installed floodmodeller_api to your active environment')
    sys.exit()

script_loc = Path(__file__).resolve().parent
os.chdir(script_loc) # Set current working directory to this script location

# Initialise ZZN class 
zzn = ZZN('sample_data/ex3.zzn')

# Export results to dataframe
results_df = zzn.to_dataframe(result_type='all')
node = 'm60' # node label for which we want the results
series = results_df['Flow'][node] # Access series data for 'm60_Flow'

print(series) # print series to console