# Import the FMTool and Parameter classes to define the tool and parameters
from __future__ import annotations

from typing import ClassVar

from floodmodeller_api.tool import FMTool, Parameter


# ------ Define function ----- #
# This is the funciton that should be run by the tool.
# In this case it is just a simple sum function but you can
# substitute any function in here.
def my_sum(a: float, b: float):
    ab = a + b
    print(ab)
    return ab


# ------ Create the Tool ------ #
class SumTool(FMTool):
    # Define the name (required):
    name = "Sum tool"
    # Add the tool description (required)
    description = "A basic tool to add two numbers together"
    # Add the parameters (one per function argument):
    parameters: ClassVar[list[Parameter]] = [
        # Add parameters using the Parameter class
        Parameter(
            name="a",
            dtype=float,
            description="the first number",
            help_text="",
            required=True,
        ),
        Parameter(
            name="b",
            dtype=float,
            description="the second number",
            help_text="",
            required=True,
        ),
    ]
    # Add the function to run
    tool_function = my_sum


if __name__ == "__main__":
    tool = SumTool()
    tool.run_from_command_line()
