import tkinter as tk
from unittest.mock import MagicMock, patch

import pytest

from floodmodeller_api.tool import FMTool, Gui, Parameter


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


# FMTool ---------


def test_check_parameters():
    # Test that the check_parameters method raises an exception when two parameters have the same name
    class MyTool(FMTool):
        name = ""
        description = ""
        tool_function = print
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


def test_run_tool_from_class(tool):
    assert tool.run(a=1, b=2) == 3


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
        "sys.argv",
        [
            "floodmodeller_api/test/test_tools.py",
            "--param1",
            "value1",
            "--param2",
            "value2",
        ],
    ):
        MyTool().run_from_command_line()


# def GUI ----------------
def test_gui_input_widgets(tool):
    tool.generate_gui()
    assert [param.name for param in tool.parameters] == [
        name for name in tool.app.root_entries.keys()
    ]


def test_gui_run_callback(tool):
    tool.generate_gui()
    tool.app.root_entries["a"].get = MagicMock(return_value=2)
    tool.app.root_entries["b"].get = MagicMock(return_value=5)
    assert tool.app.run_gui_callback() == 7


def test_gui_without_fm_tool():
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
    my_gui = Gui(
        master=tk.Tk(),
        title="My App",
        description="My Description",
        parameters=parameters,
        run_function=my_sum,
    )
    my_gui.root_entries["a"].get = MagicMock(return_value=2)
    my_gui.root_entries["b"].get = MagicMock(return_value=5)

    assert my_gui.run_gui_callback() == 7
