import argparse
from dataclasses import dataclass
import argparse
import tkinter as tk





def validate_int(value):
    # This function is used to validate integer input
    if value.isdigit():
        return True
    elif value == "":
        return True
    else:
        return False

def validate_float(value):
    # This function is used to validate float input
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
    name:str
    dtype:type
    description:str
    help_text:str
    required:bool = True

    def __eq__(self, other: object) -> bool:
        self.name == other.name

    def __hash__(self):
        return hash(self.name)
    
    def __repr__(self):
        return f"Parameter({self.name})"



class FMTool:
    parameters = []
    @property
    def name(self):
        raise NotImplementedError("Tools need a name")
    @property
    def description(self):
        raise NotImplementedError("Tools need a description")
    
    def __init__(self):
        self.check_parameters()

    def check_parameters(self):
        params = []
        for parameter in self.parameters:
            if parameter.name in params:
                raise ValueError("Parameter names must be unique")
            else: 
                params.append(parameter.name)

    # TODO: Explain why using a class method
    @classmethod
    def run(cls, **kwargs):
        cls.entry_point(**kwargs)

    def run_from_command_line(self):
        parser = argparse.ArgumentParser(description=self.description)

        for input_param in self.parameters:
            parser.add_argument(f"--{input_param.name}", required=input_param.required, help=input_param.help_text)

        args = parser.parse_args()

        input_kwargs = {}
        for input_param in self.parameters:
            input_kwargs[input_param.name] = getattr(args, input_param.name)
        print(f"Running {self.name}")
        self.run(**input_kwargs)
        print("Completed")
        
    def generate_gui(self):
        # This function generates the GUI based on the provided list of parameter names and their data types
        
        # Create the main window
        self.root = tk.Tk()
        self.root.title("Input Parameters")

        # Extract the parameters to a list to iterate through
        parameters = [(param.name, param.dtype) for param in self.parameters]

        # Create a label and entry box for each parameter
        self.root_entries = {}
        for name, data_type in parameters:
            label = tk.Label(self.root, text=name)
            label.pack()
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

        # Create the "Run" button
        run_button = tk.Button(self.root, text="Run", command=self.run_gui_callback)
        run_button.pack()


    def run_gui(self):
        self.generate_gui()
        # Start the main loop to display the GUI
        self.root.mainloop()

    def run_gui_callback(self):
        input_kwargs = {}
        for input_param in self.parameters:
            input_var = self.root_entries[input_param.name].get()
            input_var_typed = input_param.dtype(input_var)
            input_kwargs[input_param.name] = input_var_typed
        
        self.run(**input_kwargs)

