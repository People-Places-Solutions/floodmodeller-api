import argparse
import sys
from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk, filedialog as fd
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
        self.parameters = parameters
        self.run_function = run_function
        self.create_widgets(description)

    def create_widgets(self, description):
        # Icon
        path = Path(Path.cwd(), r"floodmodeller_api\toolbox\gui\icon.PNG")
        ico = Image.open(path)
        icon = ImageTk.PhotoImage(ico)
        self.master.iconphoto(False, icon)

        border = tk.Frame(
            self.master,
            width=620,
            height=403,
            highlightbackground="#0a7dff",
            highlightthickness=3,
            background="#f0f0f0",
        )
        border.place(x=0, y=-3)
        # Background image
        ##path = Path(Path.cwd(),r"floodmodeller_api\toolbox\gui\bg.PNG")
        ##img = Image.open(path)
        ##img = img.resize((int(img.width / 2.2), int(img.height / 2.2)))
        ##self.bg_image = ImageTk.PhotoImage(img)
        ##self.body_label = tk.Label(self.master, image=self.bg_image, bg="#f0f0f0")
        ##self.body_label.place(x=0, y=0)

        # Body
        # Description
        self.desc_label = ctk.CTkLabel(
            self.master,
            width=614,
            text=description,
            font=("Tahoma", 18),
            fg_color="#f0f0f0",
            compound="center",
        )
        self.desc_label.place(x=3, y=15)
        # Input sections and their labels
        self.inputs = ctk.CTkScrollableFrame(
            self.master,
            width=591,
            height=275,
            fg_color="#f0f0f0",  # "#f0f0f0",
            border_width=1,
            border_color="#f0f0f0",
            scrollbar_fg_color="#f0f0f0",
            scrollbar_button_color="#e1e1e1",
            scrollbar_button_hover_color="#b8b9bd",
        )
        self.inputs.place(x=3, y=45)
        self.add_inputs()
        # Create and place the button
        self.button = ctk.CTkButton(
            master=self.master,
            text="Run",
            font=("Tahoma", 20, "bold"),
            width=200,
            height=40,
            compound="left",
            fg_color="#0ad287",
            bg_color="#f0f0f0",
            hover_color="#6c757d",
            text_color="#f0f0f0",
            command=self.run_gui_callback,
        )
        self.button.place(x=200, y=347)

    def load_path(self, entry: ctk.CTkEntry):
        # Get file path
        file = fd.askopenfilename()  # .askdirectory()
        path = file.title()
        # Set entry text
        # entry.configure(textvariable=path)
        entry.delete(0, tk.END)
        entry.insert(0, path)

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
            set = ctk.CTkFrame(
                master=self.inputs,
                fg_color="#f0f0f0",
                border_color="#b8b9bd",
                border_width=1,
                corner_radius=0,
            )
            set.pack(pady=(3, 12))
            label = ctk.CTkLabel(
                set,
                text=f"{name}:",
                anchor="w",
                font=("Tahoma", 18),
                bg_color="#f0f0f0",
            )
            label.pack(side=tk.TOP, padx=(5, 0), pady=1, anchor="nw")

            set_bottom = tk.Frame(
                master=set,
                background="#f0f0f0",
            )
            set_bottom.pack(side=tk.BOTTOM, padx=(4, 2), pady=(0, 2))
            # Conditional stuff to add validation for different data types.
            # This ensures that you can't enter text if the input should be a number, etc.
            if data_type == str:
                entry = ctk.CTkEntry(
                    set_bottom,
                    width=400,
                    font=("Tahoma", 14),
                    border_color="#666666",
                    border_width=1,
                    corner_radius=0,
                    fg_color="#f0f0f0",
                )
            elif data_type == int:
                entry = ctk.CTkEntry(
                    set_bottom,
                    validate="key",
                    width=400,
                    font=("Tahoma", 12),
                    border_color="#919191",
                    border_width=1,
                    corner_radius=0,
                    fg_color="#f0f0f0",
                )
                entry.config(validatecommand=(entry.register(validate_int), "%P"))
            elif data_type == float:
                entry = ctk.CTkEntry(
                    set_bottom,
                    validate="key",
                    width=400,
                    font=("Tahoma", 12),
                    border_color="#919191",
                    border_width=1,
                    corner_radius=0,
                    fg_color="#f0f0f0",
                )
                entry.config(validatecommand=(entry.register(validate_float), "%P"))
            else:
                raise ValueError("Invalid data type")
            entry.pack(side=tk.LEFT)
            self.root_entries[name] = entry

            # Add the folder button
            image = Image.open(Path(Path.cwd(), r"floodmodeller_api\toolbox\gui\folder.PNG"))
            image = image.resize((int(image.width / 1), int(image.height / 1)))
            folder = ImageTk.PhotoImage(image)
            self.folder_button = ctk.CTkButton(
                master=set_bottom,
                text="",
                image=folder,
                font=("Tahoma", 20, "bold"),
                width=image.width,
                height=image.height,
                compound="left",
                fg_color="#f0f0f0",
                bg_color="#f0f0f0",
                hover_color="#999",
                text_color="#f0f0f0",
                command=lambda entry=entry: self.load_path(entry),
            )
            self.folder_button.pack(side=tk.RIGHT, padx=(3,1))
        # TODO: Add a progress bar if appropriate
        # TODO: Present some useful information: either tool outputs or logs

    def run_gui_callback(self):
        """
        Method to run the gui callback function.

        This extracts the parameter values from the GUI and passes them to the run function. It is triggered using
        the run button in the GUI.
        """

        # hide elements when showing the progress bar
        # self.button.place(x=-250,y=352)
        # self.inputs.place(x=-250,y=120)
        # self.loading_bar.place(x=10,y=360)
        # self.loading_bar.start()

        input_kwargs = {}
        for input_param in self.parameters:
            # Get the parameter value but subsetting the dictionary of GUI entry points (text boxes)
            input_var = self.root_entries[input_param.name].get()
            # Assert that the value (which is initially a string) is the right type
            # insert the value to the input_kwargs dictionary to pass to the run function
            input_kwargs[input_param.name] = input_param.dtype(input_var)
        # Run the callback function

        # show elements after the progress bar/process is finished - needs to be after run_function
        # self.loading_bar.place()
        # self.button.place(x=552,y=352)
        # self.inputs.place(x=20,y=120)
        # self.loading_bar.place(x=621,y=360)
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
        # self.app.master.after(100,self.testing)
        # self.app.master.
        self.app.master.mainloop()

    def testing(self):
        print("test!!!!!!!!!!!!")
        self.app.master.after(100, self.testing)


# g = Gui(tk.Tk(), "d", "d", [], "")
# g.create_widgets()
