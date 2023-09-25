""" This function allows you to raise the minimum bed level 300mm across all sections in a DAT file (i.e siltation) """
# Import modules
from pathlib import Path

from floodmodeller_api import DAT
from floodmodeller_api.tool import FMTool, Parameter


# Define the function
def raise_section_bed_levels(dat_input: Path, dat_output: Path, siltation: float):
    dat = DAT(dat_input)  # Initialise DAT class

    for name, section in dat.sections.items():  # iterate through all river sections
        df = section.data  # get section data
        min_elevation = df["Y"].min()  # get minimum cross section elevation
        raised_bed = min_elevation + siltation  # define new lowest bed level
        df.loc[
            df["Y"] < raised_bed, "Y"
        ] = raised_bed  # Raise any levels lower than this to the new lowest level

    dat.save(dat_output)  # save updates


# Wrap the FMTool class
class AddSiltation(FMTool):
    name = "Add Siltation"
    description = (
        "Tool to add a set amount of siltation to raise bed levels of river sections in a DAT file"
    )
    parameters = [
        Parameter(
            name="dat_input",
            dtype=str,
            description="Path to input DAT file",
            help_text="Path to input DAT file",
            required=True,
        ),
        Parameter(
            name="dat_output",
            dtype=str,
            description="Path to output DAT file",
            help_text="Path to output DAT file",
            required=True,
        ),
        Parameter(
            name="siltation",
            dtype=float,
            description="Amount of siltation to raise beds (in meters)",
            help_text="Amount of siltation to raise beds (in meters)",
            required=True,
        ),
    ]
    tool_function = raise_section_bed_levels
