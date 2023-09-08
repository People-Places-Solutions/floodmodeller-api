""" This function allows you to raise the minimum bed level 300mm across all sections in a DAT file (i.e siltation) """
# Import modules
from pathlib import Path
from floodmodeller_api import DAT
from floodmodeller_api.tool import FMTool, Parameter


## Define the function ----------------- #
def raise_section_bed_levels(dat_input: Path, dat_output: Path, min_level_m: float):
    dat = DAT(dat_input)  # Initialise DAT class

    for name, section in dat.sections.items():  # iterate through all river sections
        df = section.data  # get section data
        min_elevation = df["Y"].min()  # get minimum cross section elevation
        raised_bed = min_elevation + min_level_m  # define new lowest bed level
        df.loc[
            df["Y"] < raised_bed, "Y"
        ] = raised_bed  # Raise any levels lower than this to the new lowest level

    dat.save(dat_output)  # save updates


## Wrap the FMTool class ---------------- #
class RaiseBedLevelsTool(FMTool):
    name = "Raise Bed Levels Tool"
    description = "Tool to raise bed levels of river sections in a DAT file"
    parameters = [
        Parameter(
            name="dat_input",
            dtype=str,
            description="Path to input DAT file",
            help_text="Not helpful text",
            required=True,
        ),
        Parameter(
            name="dat_output",
            dtype=str,
            description="Path to output DAT file",
            help_text="Not helpful text",
            required=True,
        ),
        Parameter(
            name="min_level_m",
            dtype=float,
            description="Minimum bed level to raise to (in meters)",
            help_text="Not helpful text",
            required=True,
        ),
    ]
    tool_function = raise_section_bed_levels


if __name__ == "__main__":
    tool = RaiseBedLevelsTool()
    tool.run_from_command_line()
