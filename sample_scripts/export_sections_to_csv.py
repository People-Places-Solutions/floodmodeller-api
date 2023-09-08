""" This sample script shows how all the river cross sections in a DAT file can be exported into csv format """

# Import modules
import sys
import os
from glob import glob
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

# Set workspace path

for datfile in glob("sample_data/*.dat"):  # Iterate through all dat files in sample folder
    dat = DAT(datfile)  # Initialise DAT class object
    csv_out = f"sample_data/{os.path.basename(datfile)}_output_sections.csv"  # Specify output CSV
    with open(csv_out, "w", newline="") as csvfile:
        for name, section in dat.sections.items():  # Iterate through all river sections
            csvfile.write(name + "\n")  # write section name to csv
            csvfile.write(section.data.to_csv(index=False))  # write section data to csv
