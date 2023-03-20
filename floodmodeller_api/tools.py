import argparse
from dataclasses import dataclass
import argparse
from floodmodeller_api.gui import generate_gui


@dataclass()
class Parameter:
    name:str
    dtype:type
    description:str
    help_text:str
    required:bool

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

    def run(self, **kwargs):
        self.entry_point(**kwargs)

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

    def run_gui(self):
        parameters = [(param.name, param.dtype) for param in self.parameters]
        generate_gui(parameters, run_function = self.run_gui_callback)

    def run_gui_callback(self):
        input_kwargs = {}
        for input_param in self.parameters:
            input_kwargs[input_param.name] = input_param.entry.get()
        
        self.run(**input_kwargs)
