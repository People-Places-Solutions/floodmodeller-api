"""This function allows you to raise the minimum bed level 300mm across all sections in a DAT file (i.e siltation)"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from floodmodeller_api import DAT
from floodmodeller_api.tool import FMTool, Parameter
from floodmodeller_api.units import RIVER

if TYPE_CHECKING:
    from pathlib import Path


# Define the function
def raise_section_bed_levels(dat_input: Path, dat_output: Path, siltation: float):
    dat = DAT(dat_input)  # Initialise DAT class

    for section in dat.sections.values():  # iterate through all river sections
        if not isinstance(section, RIVER):
            # Skip any non river type units (e.g. interpolates)
            continue
        section_data = section.data  # get section data
        min_elevation = section_data["Y"].min()  # get minimum cross section elevation
        raised_bed = min_elevation + siltation  # define new lowest bed level
        section_data.loc[
            section_data["Y"] < raised_bed,
            "Y",
        ] = raised_bed  # Raise any levels lower than this to the new lowest level

    dat.save(dat_output)  # save updates


# Wrap the FMTool class
class AddSiltation(FMTool):
    """
    This tool allows you to add a set amount of siltation to raise the minimum bed levels of all
    river sections in a DAT file

    Args:
        dat_input (str): Path to the input DAT file
        siltation (float): Amount of siltation to raise beds (in meters)
        dat_output (str): Path to the output DAT file


    **Usage**

    To use this tool, you can either run it from the command line:

    .. code::

        fmapi-add_siltation --dat_input "<dat file path>" --siltation 0.3 --dat_output "<dat file output path>"

    Or as a gui:

    .. code::

        fmapi-add_siltation gui

    Or you can use it from your code:

    .. code:: python

        from floodmodeller_api.toolbox import AddSiltation

        AddSiltation.run(
            dat_input="path/to/dat.dat",
            siltation=0.3,
            dat_output="path/to/output_dat.dat",
        )
    """

    name = "Add Siltation"
    description = (
        "Tool to add a set amount of siltation to raise bed levels of river sections in a DAT file"
    )
    parameters: ClassVar[list[Parameter]] = [
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


def main():
    AddSiltation().run_from_command_line()
