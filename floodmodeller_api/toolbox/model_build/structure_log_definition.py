from __future__ import annotations

from typing import ClassVar

from floodmodeller_api.tool import FMTool, Parameter

from .structure_log import StructureLogBuilder


class StructureLog(FMTool):
    """
    This tool creates an output log (.csv file) of all the conduits and structures within a DAT file.
    It lists:

    - Unit Name
    - Unit Type
    - Unit Subtype
    - Comment
    - Friction
    - Distance (m)
    - Weir Coefficient
    - Culvert Inlet/Outlet Loss

    Args:
        input_path (str): Path to the input DAT file
        output_path (str): Path to the output csv file


    **Usage**

    To use this tool, you can either run it from the command line:

    .. code::

        fmapi-structure_log --input_path "<dat file path>" --output_path "<give a file path to a csv>"

    Or as a gui:

    .. code::

        fmapi-structure_log gui

    Or you can use it from your code:

    .. code:: python

        from floodmodeller_api.toolbox import StructureLog

        StructureLog.run(
            input_path="path/to/dat.dat",
            output_path="path/to/csv.csv",
        )
    """

    name = "Structure Log"
    description = "Creates a structure log"
    parameters: ClassVar[list[Parameter]] = [
        Parameter(
            name="input_path",
            dtype=str,
            description="Path to input DAT file",
            help_text="Where the DAT file will be read from",
            required=True,
        ),
        Parameter(
            name="output_path",
            dtype=str,
            description="Path to output csv",
            help_text="Where the new model will be saved (csv must be closed)",
            required=True,
        ),
    ]

    @classmethod
    def tool_function(cls, **kwargs):
        return StructureLogBuilder(**kwargs).create()


def main():
    StructureLog().run_from_command_line()
