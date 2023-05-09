from floodmodeller_api.tool import FMTool, Parameter
from .helpers.model_converter import TuflowModelConverter2D


class Tuflow2DConversionTool(FMTool):
    name = "TUFLOW 2D Conversion Tool"
    description = "Convert 2D models"
    parameters = [
        Parameter(
            name="tcf_path",
            dtype=str,
            description="Path to input TCF file",
            help_text="Where the TCF file will be read from",
            required=True,
        ),
        Parameter(
            name="xml_path",
            dtype=str,
            description="Path to output XML file",
            help_text="Where the XML file will be saved",
            required=True,
        ),
        Parameter(
            name="ief_path",
            dtype=str,
            description="Path to output IEF file",
            help_text="Where the IEF file will be saved",
            required=True,
        ),
        Parameter(
            name="inputs_name",
            dtype=str,
            description="Path to output processed GIS files",
            help_text="Where the process GIS files will be saved",
            required=True,
        ),
        Parameter(
            name="log_path",
            dtype=str,
            description="Path to output log file",
            help_text="Where the log file will be saved",
            required=True,
        ),
    ]
    tool_function = lambda **kwargs: TuflowModelConverter2D(**kwargs).convert_model()
