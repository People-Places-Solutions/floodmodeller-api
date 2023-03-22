import argparse
from dataclasses import dataclass
import argparse
import tkinter as tk

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
    name:str
    dtype:type
    description:str = None
    help_text:str = None
    required:bool = True

    def __eq__(self, other: object) -> bool:
        self.name == other.name

    def __hash__(self):
        return hash(self.name)
    
    def __repr__(self):
        return f"Parameter({self.name})"



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
        # Create an argument parse and add each argument defined in the parameters
        parser = argparse.ArgumentParser(description=self.description)
        # Add each param as an argument
        for input_param in self.parameters:
            parser.add_argument(f"--{input_param.name}", required=input_param.required, help=input_param.help_text)
        
        # Parse the aruments from the commandline
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
        # This function generates the GUI based on the provided list of parameter names and their data types
        """
        Method to generate a Tkinter graphical user interface (GUI) for the tool.

        This method generates a GUI based upon the function parameters, allowing any tool  to be 
        run from a GUI rather than as python code. The method adds the GUI root as a class attribute
        """
        # Create the main window
        self.root = tk.Tk()
        self.root.title("Input Parameters")

        # Extract the parameters to a list to iterate through
        parameters = [(param.name, param.dtype) for param in self.parameters]

        # Create a label and entry box for each parameter
        # Adding the input boxes as a class attribute dictionary 
        # this enables us to easily get the values of in each input box and pass them to 
        # the run function. It also makes it easier to debug since you can create an instance, generate the GUI
        # and then inspect the attributes.
        self.root_entries = {}
        for name, data_type in parameters:
            label = tk.Label(self.root, text=name)
            label.pack()
            # Conditional stuff to add validation for different data types.
            # This ensures that you can't enter text if the input should be a number, etc.
            if data_type == str:
                entry = tk.Entry(self.root)
            elif data_type == int:
                entry = tk.Entry(self.root, validate="key")
                entry.config(validatecommand=(entry.register(validate_int), "%P"))
            elif data_type == float:
                entry = tk.Entry(self.root, validate="key")
                entry.config(validatecommand=(entry.register(validate_float), "%P"))
            else:
                raise ValueError("Invalid data type")
            entry.pack()
            self.root_entries[name] = entry
        
        # TODO: Add some formatting to improve GUI
        # TODO: Add tool name, description etc
        # TODO: Add a progress bar if appropriate
        # TODO: Present some useful information: either tool outputs or logs

        # Create the "Run" button
        run_button = tk.Button(self.root, text="Run", command=self.run_gui_callback)
        run_button.pack()


    def run_gui(self):
        """
        Method to run the GUI
        """
        self.generate_gui()
        # Start the main loop to display the GUI
        self.root.mainloop()

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
        return self.run(**input_kwargs)

