from __future__ import annotations

import argparse
import logging
import sys
import tkinter as tk
from dataclasses import dataclass
from typing import ClassVar


@dataclass()
class Parameter:
    """Class to represent an FM Tool parameter.
    There should be one parameter for each argument of the tool_function function

    Args:
        name (str): The name of the parameter.
        dtype (type): The expected data type of the parameter.
        description (str): A description of the parameter.
        help_text (str): The help text to be displayed for the parameter.
        required (bool): A flag indicating whether the parameter is required or optional. Default is True.

    Methods:
        __eq__: Compare two parameters by their name attribute.
        __hash__: Return the hash value of the parameter name.
        __repr__: Return a string representation of the parameter.

    """

    name: str
    dtype: type
    description: str | None = None
    help_text: str | None = None
    required: bool = True

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Parameter):
            return NotImplemented
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return f"Parameter({self.name})"


def validate_int(value):
    """Function to validate integer input.

    Args:
        value (str): The input value to be validated.

    Returns:
        bool: True if input value is a valid integer or an empty string, False otherwise.
    """
    if value.isdigit():
        return True
    return value == ""


def validate_float(value):
    """Function to validate float input.

    Args:
        value (str): The input value to be validated.

    Returns:
        bool: True if input value is a valid float or an empty string, False otherwise.
    """
    try:
        float(value)
        return True
    except ValueError:
        return value == ""


class Gui:
    """
    Method to generate a Tkinter graphical user interface (GUI).
    This method generates a GUI based upon a function, its parameters, as well as descriptive properties  allowing any tool  to be
    run from a GUI rather than as python code.

    Args:
        master (tkinter.Tk): a tkinter root object. Contains app methods and attributes
        title (str): The Apps title
        description (str): A description of the application
        parameters (list[Parameter]): a list of parameters. This is used to generate the input boxes and pass kwargs to the run function
        run_function (function): a function that should be run by the app

    """

    def __init__(
        self,
        master: tk.Tk,
        title: str,
        description: str,
        parameters: list[Parameter],
        run_function,
    ):
        self.master = master
        self.master.title(title)
        self.master.geometry("400x300")
        self.master.configure(bg="#f5f5f5")
        self.parameters = parameters
        self.run_function = run_function
        self.create_widgets(description)

    def create_widgets(self, description):
        # Create and place the description label
        desc_label = tk.Label(self.master, text=description, font=("Arial", 14), bg="#f5f5f5")
        desc_label.pack(pady=(20, 10))
        # Run the method to add inputs based upon parameters
        self.add_inputs()
        # Create and place the button
        self.button = tk.Button(
            self.master,
            text="Run",
            font=("Arial", 14),
            command=self.run_gui_callback,
        )
        self.button.pack(pady=10)
        # Add other widgets to the app
        ###

    def add_inputs(self):
        """
        Method to add inputs widgets to the app based upon parameters.

        This method adds an input widget to the app for each parameter.
        """
        # Extract the parameters to a list to iterate through
        parameters = [(param.name, param.dtype) for param in self.parameters]

        # Create a label and entry box for each parameter
        # Adding the input boxes as a class attribute dictionary
        # this enables us to easily get the values of in each input box and pass them to
        # the run function. It also makes it easier to debug since you can create an instance, generate the GUI
        # and then inspect the attributes.
        self.root_entries = {}
        for name, data_type in parameters:
            label = tk.Label(self.master, text=name, anchor="w")
            label.pack()
            # Conditional stuff to add validation for different data types.
            # This ensures that you can't enter text if the input should be a number, etc.
            if data_type is str:
                entry = tk.Entry(self.master)
            elif data_type is int:
                entry = tk.Entry(self.master, validate="key")
                entry.config(validatecommand=(entry.register(validate_int), "%P"))
            elif data_type is float:
                entry = tk.Entry(self.master, validate="key")
                entry.config(validatecommand=(entry.register(validate_float), "%P"))
            else:
                msg = "Invalid data type"
                raise ValueError(msg)
            entry.pack()
            self.root_entries[name] = entry

    def run_gui_callback(self):
        """
        Method to run the gui callback function.

        This extracts the parameter values from the GUI and passes them to the run function. It is triggered using
        the run button in the GUI.
        """
        input_kwargs = {}
        for input_param in self.parameters:
            # Get the parameter value but subsetting the dictionary of GUI entry points (text boxes)
            input_var = self.root_entries[input_param.name].get()
            # Assert that the value (which is initially a string) is the right type
            # insert the value to the input_kwargs dictionary to pass to the run function
            input_kwargs[input_param.name] = input_param.dtype(input_var)
        # Run the callback function
        return self.run_function(**input_kwargs)


class FMTool:
    """
    Compare two parameters by their name attribute.

    Use the class by wrapping it in a child class which defines the parameters and function to call:

    This class provides a consistent method to structure flood modeller tools that
    use the API to automate processes, extract data and visualise results. The class also provides
    methods to extend any tool with a command line interface or tkinter GUI.

    We plan to add more extensions in the future.

    Args:
        name (str): The name of the tool to display in the GUI or cmd line
        description (str): A description of the tool and what it does.
        parameters (list[Parameter]): the Tool parameters, one per input function
        tool_function (function): The function to be called by the tool

    .. code:: python

        # concatenates strings
        def concat(str1, str2):
            return str1 + str2
        class MyTool(FMTool):
            name = "Name"
            description = "Tool description"
            parameters = [
                Parameter("str1", str),
                Parameter("str2", str)
            ]
            tool_function = concat

    """

    parameters: ClassVar[list[Parameter]] = []

    @property
    def name(self):
        """
        A property method to ensure a tool name is provided in child class. Overwritten by child.
        """
        msg = "Tools need a name"
        raise NotImplementedError(msg)

    @property
    def description(self):
        """
        A property method to ensure a tool description is provided in child class. Overwritten by child.
        """
        msg = "Tools need a description"
        raise NotImplementedError(msg)

    @property
    def tool_function(self):
        """
        A property method to ensure an tool_function is provided in child class. Overwritten by child.
        """
        msg = "You must provide an entry point function"
        raise NotImplementedError(msg)

    def __init__(self):
        self.check_parameters()

    def check_parameters(self):
        """
        A function to check that all parameter names are unique.

        Since parameter names correspond to function arguments, this function is required to check that all
        are unique.

        Raises:
            ValueError: if parameter names aren't unique
        """
        params = []
        for parameter in self.parameters:
            if parameter.name in params:
                msg = "Parameter names must be unique"
                raise ValueError(msg)
            params.append(parameter.name)

    # This is defined as a class method because of the use of **kwargs
    # When using this approach to pass around function arguments, the self object is appended to the **kwargs
    # passed into the function and this results in the wrong number of arguments being passed to the tool_function function
    @classmethod
    def run(cls, **kwargs):
        """
        Method to run the entry point function.

        This approach allows the function to be run either from the command line interface, the GUI or any other extensions
        that we add in the future.
        Args:
            **kwargs: keyword arguments for the tool_function function.
        """
        return cls.tool_function(**kwargs)

    def run_from_command_line(self):
        """
        Method to run the tool from the command line.

        This method parses command line arguments (as defined in self.parameters) and passes them to run to execute the tool
        """
        run_gui = False
        try:
            if sys.argv[1] == "gui":
                # gui flag added so running as gui
                run_gui = True
        except IndexError:
            pass

        if run_gui:
            self.run_gui()
            return

        # Create an argument parse and add each argument defined in the parameters
        parser = argparse.ArgumentParser(description=self.description)

        # Parse the aruments from the commandline
        for input_param in self.parameters:
            parser.add_argument(
                f"--{input_param.name}",
                required=input_param.required,
                help=input_param.help_text,
            )

        args = parser.parse_args()
        # And then construct a dictionary of them that can be passed to the run function as keyword arguments
        input_kwargs = {}
        for input_param in self.parameters:
            value = getattr(args, input_param.name)
            input_kwargs[input_param.name] = input_param.dtype(value)

        logging.info("Running %s", self.name)
        self.run(**input_kwargs)
        logging.info("Completed")
        # Return nothing

    def generate_gui(self):
        """
        Method to build the GUI
        """
        root = tk.Tk()
        self.app = Gui(
            root,
            title=self.name,
            description=self.description,
            parameters=self.parameters,
            run_function=self.run,
        )

    def run_gui(self):
        """
        Method to run the GUI
        """
        self.generate_gui()
        self.app.master.mainloop()
