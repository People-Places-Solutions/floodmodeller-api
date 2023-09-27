import argparse
import sys
import tkinter as tk
from tkinter import ttk, filedialog as fd, messagebox
from pathlib import Path
from PIL import Image, ImageTk
import customtkinter as ctk
import traceback
import io
import threading
from dataclasses import dataclass


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
        self.create_input_widgets(description)

    def create_input_widgets(self, description):
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
        self.running = False
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
            command=self.button_pressed,
        )
        self.button.place(x=200, y=347)

    def load_file_path(self, entry: ctk.CTkEntry):
        file = fd.askopenfilename()
        path = file.title()
        entry.delete(0, tk.END)
        entry.insert(0, path)

    def load_folder_path(self, entry: ctk.CTkEntry):
        folder = fd.askdirectory()
        path = folder.title()
        entry.delete(0, tk.END)
        entry.insert(0, path)

    def show_help(self, name, text):
        messagebox.showinfo(f"Input Help: {name}", text)

    def add_inputs(self):
        """
        Method to add inputs widgets to the app based upon parameters.

        This method adds an input widget to the app for each parameter.
        """
        # Extract the parameters to a list to iterate through
        parameters = [[param.name, param.dtype, param.help_text] for param in self.parameters]

        # Create a label and entry box for each parameter
        # Adding the input boxes as a class attribute dictionary
        # this enables us to easily get the values of in each input box and pass them to
        # the run function. It also makes it easier to debug since you can create an instance, generate the GUI
        # and then inspect the attributes.
        self.root_entries = {}
        for name, data_type, help_text in parameters:
            set = ctk.CTkFrame(
                master=self.inputs,
                fg_color="#f0f0f0",
                border_color="#b8b9bd",
                border_width=1,
                corner_radius=0,
            )
            set.pack(pady=(3, 12))
            set_top = tk.Frame(master=set, background="#f0f0f0", width=600)
            set_top.pack(side=tk.TOP, pady=(3, 0), padx=(1, 3), fill="both", expand=True)
            label = ctk.CTkLabel(
                set_top,
                text=f"{name}:",
                anchor="w",
                font=("Tahoma", 18),
                bg_color="#f0f0f0",
            )
            label.pack(side=tk.LEFT, padx=(5, 0), pady=1, anchor="nw")
            image = Image.open(Path(Path.cwd(), r"floodmodeller_api\toolbox\gui\help.PNG"))
            image = image.resize((int(image.width / 1), int(image.height / 1)))
            folder = ImageTk.PhotoImage(image)
            self.help_button = ctk.CTkButton(
                master=set_top,
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
                command=lambda name=name, help_text=help_text: self.show_help(name, help_text),
            )
            self.help_button.pack(side=tk.RIGHT, anchor="ne")

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
                    border_color="#000",
                    border_width=1,
                    corner_radius=0,
                    fg_color="#fff",
                )
            elif data_type == int:
                entry = ctk.CTkEntry(
                    set_bottom,
                    validate="key",
                    width=400,
                    font=("Tahoma", 12),
                    border_color="#000",
                    border_width=1,
                    corner_radius=0,
                    fg_color="#fff",
                )
                entry.config(validatecommand=(entry.register(validate_int), "%P"))
            elif data_type == float:
                entry = ctk.CTkEntry(
                    set_bottom,
                    validate="key",
                    width=400,
                    font=("Tahoma", 12),
                    border_color="#000",
                    border_width=1,
                    corner_radius=0,
                    fg_color="#fff",
                )
                entry.config(validatecommand=(entry.register(validate_float), "%P"))
            else:
                raise ValueError("Invalid data type")
            entry.pack(side=tk.LEFT)
            self.root_entries[name] = entry

            # Add the file button
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
                command=lambda entry=entry: self.load_folder_path(entry),
            )
            self.folder_button.pack(side=tk.RIGHT, padx=(0, 1))
            image = Image.open(Path(Path.cwd(), r"floodmodeller_api\toolbox\gui\file.PNG"))
            image = image.resize((int(image.width / 1), int(image.height / 1)))
            folder = ImageTk.PhotoImage(image)
            self.file_button = ctk.CTkButton(
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
                command=lambda entry=entry: self.load_file_path(entry),
            )
            self.file_button.pack(side=tk.RIGHT, padx=(6, 1))
        # TODO: Add a progress bar if appropriate
        # TODO: Present some useful information: either tool outputs or logs

    def button_pressed(self):
        self.clear_input_widgets()
        self.show_running_page()
        self.running = True

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
        self.run_function(**input_kwargs)  # return?

    def clear_input_widgets(self):
        self.desc_label.place_forget()
        self.inputs.place_forget()
        self.button.place_forget()

    def show_running_page(self):
        self.running_label = ctk.CTkLabel(
            master=self.master,
            text="Running...",
            font=("Tahoma", 20),
            bg_color="#f0f0f0",
        )
        self.running_label.place(x=260, y=10)
        self.buffer_outputs = ctk.CTkScrollableFrame(
            self.master,
            width=587,
            height=275,
            fg_color="#fff", # "#f0f0f0",
            border_width=1,
            border_color="#000",
            scrollbar_fg_color="#f0f0f0",
            scrollbar_button_color="#e1e1e1",
            scrollbar_button_hover_color="#b8b9bd",
        )
        self.buffer_text = ""
        self.buffer_label = ctk.CTkLabel(master=self.buffer_outputs, width=570, text=self.buffer_text, font=("Tahoma", 16,), wraplength=570, justify="left")
        self.buffer_outputs.place(x=5, y=45)

    def finished_running(self):
        self.return_button = ctk.CTkButton(
            master=self.master,
            text="Return",
            font=("Tahoma", 20, "bold"),
            width=200,
            height=40,
            compound="left",
            fg_color="#0ad287",
            bg_color="#f0f0f0",
            hover_color="#6c757d",
            text_color="#f0f0f0",
            command=self.clear_running_page,
        )
        self.return_button.place(x=200, y=347)

    def clear_running_page(self):
        self.running_label.place_forget()
        self.buffer_outputs.place_forget()
        self.return_button.place_forget()
        self.show_input_widgets()

    def show_input_widgets(self):
        self.desc_label.place(x=3, y=15)
        self.inputs.place(x=3, y=45)
        self.button.place(x=200, y=347)


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
            value = getattr(args, input_param.name)
            input_kwargs[input_param.name] = input_param.dtype(value)

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
        self.app.master.after(100, self.run_tool)
        self.app.master.mainloop()

    def run_tool(self):
        if self.app.running:
            self.app.running = False
            old_stdout = sys.stdout
            buffer = TextRedirector(self.app.buffer_text, self.app.buffer_label)#self.app.buffer_text, self.app.buffer_label)
            sys.stdout = buffer # buffer = TextRedirector(self.app.buffer_text, self.app.buffer_label)
            try:
                self.app.run_gui_callback()
            except Exception as error:
                print(traceback.format_exc())
            sys.stdout = old_stdout
            #what_was_printed = buffer.get_console_output()
            print("@@@@@@@@@@")
            print(buffer.get_console_output() + "###")
            self.app.finished_running()
        self.app.master.after(200, self.run_tool)


class TextRedirector(object):
    def __init__(self, buffer_text, buffer_label: ctk.CTkLabel):#, buffer_label: ctk.CTkLabel) -> None:
        self.label = buffer_label
        self.buffer_text = buffer_text

    def write(self, str_input):
        self.buffer_text += f"{str_input}"
        self.label["text"] = self.buffer_text

    def get_console_output(self):
        return self.buffer_text
