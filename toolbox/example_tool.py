from floodmodeller_api.tools import FMTool, Parameter

# ------ Define function ----- #
def my_sum(a : float, b : float):
    ab = a + b
    print(ab)
    return ab


class SumTool(FMTool):
    # Define the name 
    name = "Sum tool"
    description = "A basic tool to add two numbers together"
    parameters = [
        Parameter(name = "a", dtype = float, description="the first number", help_text="", required=True),
        Parameter(name = "b", dtype = float, description="the second number", help_text="", required=True)
    ]
    entry_point = my_sum


if __name__ == "__main__":
    tool = SumTool()
    tool.run_from_command_line()

