from floodmodeller_api.tools import FMTool, Parameter
import pytest
from unittest.mock import patch


# ------ Define function ----- #
def my_sum(a: float, b: float):
    ab = a + b
    print(ab)
    return ab


class SumTool(FMTool):
    # Define the name
    name = "Sum tool"
    description = "A basic tool to add two numbers together"
    parameters = [
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
    tool_function = my_sum


@pytest.fixture
def tool():
    return SumTool()


def test_function_works(tool):
    assert tool.run(a=1, b=2) == 3


def test_tool_functions(tool):
    tool.generate_gui()
    [param.name for param in tool.parameters] == [
        name for name in tool.root_entries.keys()
    ]


def test_check_parameters():
    # Test that the check_parameters method raises an exception when two parameters have the same name
    class MyTool(FMTool):
        parameters = [
            Parameter(
                name="param1",
                dtype=str,
                description="Description 1",
                help_text="Help text 1",
            ),
            Parameter(
                name="param1",
                dtype=str,
                description="Description 2",
                help_text="Help text 2",
            ),
        ]

    with pytest.raises(ValueError):
        MyTool()


def test_run():
    # Test that the run method calls the tool_function method with the correct arguments
    class MyTool(FMTool):
        @classmethod
        def tool_function(cls, param1, param2):
            assert param1 == "value1"
            assert param2 == "value2"

    MyTool.run(param1="value1", param2="value2")


def test_run_from_command_line():
    # Test that the run_from_command_line method parses the command line arguments correctly
    class MyTool(FMTool):
        name = "My Tool"
        description = "My Tools Description"
        parameters = [Parameter("param1", str), Parameter("param2", str)]

        @classmethod
        def tool_function(cls, param1, param2):
            assert param1 == "value1"
            assert param2 == "value2"

    with patch(
        "sys.argv", ["floodmodeller_api/test/test_tools.py", "--param1", "value1", "--param2", "value2"]
    ):
        MyTool().run_from_command_line()



def test_generate_gui():
    # Test that the generate_gui method creates the correct widgets
    class MyTool(FMTool):
        parameters = [
            Parameter(
                name="param1",
                dtype=str,
                description="Description 1",
                help_text="Help text 1",
            ),
            Parameter(
                name="param2",
                dtype=int,
                description="Description 2",
                help_text="Help text 2",
            ),
        ]

    tool = MyTool()
    tool.generate_gui()

    # Check that the window title is correct
    assert tool.root.title() == "Input Parameters"

    # Check that there is a label and an entry box for each parameter
    assert len(tool.root_entries) == 2
    assert tool.root_entries["param1"].winfo_class() == "Entry"
    assert tool.root_entries["param2"].winfo_class() == "Entry"


def test_run_gui_callback():
    # Test that the run_gui_callback method reads the input values from the GUI correctly
    class MyTool(FMTool):
        parameters = [
            Parameter(
                name="param1",
                dtype=str,
                description="Description 1",
                help_text="Help text 1",
            ),
            Parameter(
                name="param2",
                dtype=int,
                description="Description 2",
                help_text="Help text 2",
            ),
        ]

        @classmethod
        def tool_function(cls, param1, param2):
            assert param1 == "value1"
            assert param2 == 42

    tool = MyTool()
    tool.generate_gui()

    # Set the values of the input widgets
    tool.root_entries["param1"].insert(0, "value1")
    tool.root_entries["param2"].insert(0, "42")

    # Call the callback function and check that the tool_function method is called with the correct arguments
    with patch.object(tool, "run") as mock_run:
        tool.run_gui_callback()
        mock_run.assert_called_once_with(param1="value1", param2=42)
