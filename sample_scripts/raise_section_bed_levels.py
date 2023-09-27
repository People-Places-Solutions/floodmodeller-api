""" This sample script shows how you could raise the minimum bed level 300mm across all sections in a DAT file (i.e siltation) """

# Import modules
import os
import sys
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

dat = DAT("sample_data\\ex3.dat")  # Initialise DAT class

for name, section in dat.sections.items():  # iterate through all river sections
    df = section.data  # get section data
    min_elevation = df["Y"].min()  # get minimum cross section elevation
    raised_bed = min_elevation + 0.3  # define new lowest bed level (+300mm)
    df.loc[
        df["Y"] < raised_bed, "Y"
    ] = raised_bed  # Raise any levels lower than this to the new lowest level

dat.save("sample_data\\ex3_300m_siltation.dat")  # save updates
