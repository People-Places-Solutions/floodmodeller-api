import tkinter as tk
from tkinter import messagebox


def generate_gui(parameter_names_and_types, run_function):
    # This function generates the GUI based on the provided list of parameter names and their data types
    
    # Create the main window
    root = tk.Tk()
    root.title("Input Parameters")

    # Create a label and entry box for each parameter
    entries = []
    for name, data_type in parameter_names_and_types:
        label = tk.Label(root, text=name)
        label.pack()
        if data_type == str:
            entry = tk.Entry(root)
        elif data_type == int:
            entry = tk.Entry(root, validate="key")
            entry.config(validatecommand=(entry.register(validate_int), "%P"))
        elif data_type == float:
            entry = tk.Entry(root, validate="key")
            entry.config(validatecommand=(entry.register(validate_float), "%P"))
        else:
            raise ValueError("Invalid data type")
        entry.pack()
        entries.append(entry)

    # Create the "Run" button
    run_button = tk.Button(root, text="Run", command=run_function)
    run_button.pack()

    # Start the main loop to display the GUI
    root.mainloop()

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

# Example usage
# parameter_names_and_types = [("Parameter 1", int), ("Parameter 2", float), ("Parameter 3", str)]
# generate_gui(parameter_names_and_types)

def print_sum(param_1, param_2):
    print(sum([param_1, param_2]))

generate_gui([("param_1", int), ("param_2", int)], print_sum)
