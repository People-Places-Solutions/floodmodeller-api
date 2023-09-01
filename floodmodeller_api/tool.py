import argparse
import sys
from dataclasses import dataclass
import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk
import customtkinter as ctk


@dataclass()
class Parameter:
    """Class to represent an FM Tool parameter.
    There should be one parameter for each argument of the tool_function function

    Attributes:
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
    description: str = None
    help_text: str = None
    required: bool = True

    def __eq__(self, other: object) -> bool:
        self.name == other.name

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
    elif value == "":
        return True
    else:
        return False


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
        if value == "":
            return True
        else:
            return False


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
        self.master.geometry("620x400")
        self.master.resizable(False, False)
        self.master.configure(bg="#ffffff")
        self.parameters = parameters
        self.run_function = run_function
        self.create_widgets(description)

    def create_widgets(self, description):
        # Background image
        path = Path.joinpath(Path.cwd(),r"C:\FloodModellerJacobs\floodmodeller-api\floodmodeller_api\toolbox\gui\bg.PNG")
        img = Image.open(path)
        img = img.resize((int(img.width / 2.2), int(img.height / 2.2)))
        self.bg_image = ImageTk.PhotoImage(img)
        self.body_label = tk.Label(self.master, image=self.bg_image, bg="#ffffff")
        self.body_label.place(x=-20, y=21)

        # Banner
        # FM logo
        path = Path.joinpath(Path.cwd(),r"C:\FloodModellerJacobs\floodmodeller-api\floodmodeller_api\toolbox\gui\logo.PNG")
        img = Image.open(path)
        img = img.resize((int(img.width / 2), int(img.height / 2)))
        self.logo = ImageTk.PhotoImage(img)
        self.logo_label = tk.Label(self.master, image=self.logo, bg="#ffffff")
        self.logo_label.place(x=10, y=5)
        # API
        self.api_label = tk.Label(
            self.master, text="API", font=("Dubai Medium", 18), bg="#ffffff"
        )
        self.api_label.place(x=570, y=5)
        # Separator
        self.separator = tk.Canvas(self.master, width=800, height=20, bg="#0a7dff")
        self.separator.place(x=-5, y=50)

        # Body
        # Description
        self.desc_label = tk.Label(
            self.master, text=description, font=("Dubai Medium", 18), bg="#ffffff"
        )
        self.desc_label.place(x=10, y=75)
        # Input sections and their labels
        self.inputs = ctk.CTkScrollableFrame(
            self.master,
            width=190,
            height=250,
            fg_color="#ffffff",
            border_width=2,
            border_color="gray50",
            scrollbar_fg_color="gray85",
        )
        self.inputs.place(x=20, y=120)
        self.add_inputs()
        # Create and place the button
        self.button = ctk.CTkButton(
            master=self.master,
            text="Run",
            font=("Dubai Medium", 20, "bold"),
            width=60,
            height=40,
            compound="left",
            fg_color="#0a7dff",
            bg_color="#ffffff",
            hover_color="#80bbff",
            text_color="#ffffff",
            command=self.run_gui_callback,
        )
        self.button.place(x=552, y=352)
        # Loading bar - needs to move along as conversion progresses... colour change?
        #self.loading_bar = ctk.CTkProgressBar(
        #    self.master,
        #    width=605,
        #    height=30,
        #)

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
            label = ctk.CTkLabel(
                self.inputs,
                text=name,
                anchor="w",
                font=("Dubai Medium", 18),
                bg_color="#ffffff"
            )
            label.pack(padx=3,pady=3)
            # Conditional stuff to add validation for different data types.
            # This ensures that you can't enter text if the input should be a number, etc.
            if data_type == str:
                entry = ctk.CTkEntry(
                    self.inputs,
                    width=400,
                    border_width=2,
                    border_color="gray50",
                    font=("Courier New", 14),
                )
            elif data_type == int:
                entry = tk.Entry(
                    self.inputs,
                    validate="key",
                    width=400,
                    border_width=2,
                    border_color="gray50",
                    font=("Courier New", 12),
                )
                entry.config(validatecommand=(entry.register(validate_int), "%P"))
            elif data_type == float:
                entry = tk.Entry(
                    self.inputs,
                    validate="key",
                    width=400,
                    border_width=2,
                    border_color="gray50",
                    font=("Courier New", 12),
                )
                entry.config(validatecommand=(entry.register(validate_float), "%P"))
            else:
                raise ValueError("Invalid data type")
            entry.pack()
            self.root_entries[name] = entry
        # TODO: Add a progress bar if appropriate
        # TODO: Present some useful information: either tool outputs or logs

    def run_gui_callback(self):
        """
        Method to run the gui callback function.

        This extracts the parameter values from the GUI and passes them to the run function. It is triggered using
        the run button in the GUI.
        """

        # hide elements when showing the progress bar
        #self.button.place(x=-250,y=352)
        #self.inputs.place(x=-250,y=120)
        #self.loading_bar.place(x=10,y=360)
        #self.loading_bar.start()

        input_kwargs = {}
        for input_param in self.parameters:
            # Get the parameter value but subsetting the dictionary of GUI entry points (text boxes)
            input_var = self.root_entries[input_param.name].get()
            # Assert that the value (which is initially a string) is the right type
            # insert the value to the input_kwargs dictionary to pass to the run function
            input_kwargs[input_param.name] = input_param.dtype(input_var)
        # Run the callback function

        # show elements after the progress bar/process is finished - needs to be after run_function
        #self.loading_bar.place()
        #self.button.place(x=552,y=352)
        #self.inputs.place(x=20,y=120)
        #self.loading_bar.place(x=621,y=360)
        return self.run_function(**input_kwargs)


class FMTool:
    """
    Compare two parameters by their name attribute.

    Use the class by wrapping it in a child class which defines the parameters and function to call:

    This class provides a consistent method to structure flood modeller tools that
    use the API to automate processes, extract data and visualise results. The class also provides
    methods to extend any tool with a command line interface or tkinter GUI.

    We plan to add more extensions in the future.

    Attributes:
        name (str): The name of the tool to display in the GUI or cmd line
        description (str): A description of the tool and what it does.
        parameters (list[Parameter]): the Tool parameters, one per input function
        tool_function (function): The function to be called by the tool

    ```
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
    ```
    """

    parameters = []

    @property
    def name(self):
        """
        A property method to ensure a tool name is provided in child class. Overwritten by child.
        """
        raise NotImplementedError("Tools need a name")

    @property
    def description(self):
        """
        A property method to ensure a tool description is provided in child class. Overwritten by child.
        """
        raise NotImplementedError("Tools need a description")

    @property
    def tool_function(self):
        """
        A property method to ensure an tool_function is provided in child class. Overwritten by child.
        """
        raise NotImplementedError("You must provide an entry point function")

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
                raise ValueError("Parameter names must be unique")
            else:
                params.append(parameter.name)

    # TODO: Explain why using a class method
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
            input_kwargs[input_param.name] = getattr(args, input_param.name)

        print(f"Running {self.name}")
        self.run(**input_kwargs)
        print("Completed")
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
        self.app.master.after(5000,self.testing)
        #self.app.master.
        self.app.master.mainloop()
    
    def testing(self):
        print("test!!!!!!!!!!!!")
