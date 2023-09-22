from floodmodeller_api.tool import FMTool, Parameter

from .structure_log.structure_log import StructureLogBuilder


class StructureLog(FMTool):
    name = "Structure Log"
    description = "Creates a structure log"
    parameters = [
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
