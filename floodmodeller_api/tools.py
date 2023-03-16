import argparse
from dataclasses import dataclass
import argparse
import tkinter as tk
from tkinter import filedialog



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
        root = tk.Tk()
        root.title(self.name)

        inputs_frame = tk.Frame(root)
        inputs_frame.pack(side='top', padx=5, pady=5)

        for input_param in self.parameters:
            label = tk.Label(inputs_frame, text=input_param.name)
            label.pack(side='left')

            if input_param.get('type', False):
                def choose_file():
                    file_path = filedialog.askopenfilename()
                    entry.delete(0, tk.END)
                    entry.insert(0, file_path)

                entry = tk.Entry(inputs_frame)
                entry.pack(side='left')

                button = tk.Button(inputs_frame, text='Choose file', command=choose_file)
                button.pack(side='left')
            else:
                entry = tk.Entry(inputs_frame)
                entry.pack(side='left')

            label.config(text=input_param.name + ' *')
            entry.config(validate='focusout', validatecommand=(entry.register(self.validate_required_entry), '%P'))

        run_button = tk.Button(root, text='Run', command=self.run_gui_callback)
        run_button.pack(side='bottom')

        root.mainloop()

    def run_gui_callback(self):
        input_kwargs = {}
        for input_param in self.parameters:
            input_kwargs[input_param.name] = input_param['entry'].get()

        self.run(**input_kwargs)

    def validate_required_entry(self, text):
        if not text:
            return False
        return True

