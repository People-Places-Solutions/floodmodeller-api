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
            name="folder",
            dtype=str,
            description="Path to new model folder",
            help_text="Where the new model will be saved",
            required=True,
        ),
        Parameter(
            name="name",
            dtype=str,
            description="Name for new model files",
            help_text="Will be used when saving new model files",
            required=True,
        ),
    ]
    tool_function = lambda **kwargs: TuflowModelConverter2D(**kwargs).convert_model()
