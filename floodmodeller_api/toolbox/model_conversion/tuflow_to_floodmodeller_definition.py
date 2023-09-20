from floodmodeller_api.tool import FMTool, Parameter

from .tuflow_to_floodmodeller.model_converter import TuflowModelConverter


class TuflowToFloodModeller(FMTool):
    name = "TUFLOW to Flood Modeller Conversion Tool"
    description = "Convert models from TUFLOW to Flood Modeller"
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
    tool_function = lambda **kwargs: TuflowModelConverter(**kwargs).convert_model()
