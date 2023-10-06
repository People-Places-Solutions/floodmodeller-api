# Flood Modeller Python API Toolbox
The API toolbox serves as a place to store and maintain tools that integrate with the Flood Modeller 
Python API, and by using a common class to define tools (`FMTool`), allows for a single tool to be used
in multiple ways e.g. from command line, imported into python code, as a simple gui or any other method
you can implement.

Tools sit under the following categories:
|Category | Description |
|---------|-------------|
|[Results Analysis](https://github.com/People-Places-Solutions/floodmodeller-api/tree/main/toolbox/results_analysis)| Tools aimed at analysing and visualising model results
|[Model Build](https://github.com/People-Places-Solutions/floodmodeller-api/tree/main/toolbox/model_build)| Tools to support model build activities
|[Model Conversion](https://github.com/People-Places-Solutions/floodmodeller-api/tree/main/toolbox/model_conversion)| Tools to convert models from other packages into Flood Modeller format
|[Model Review](https://github.com/People-Places-Solutions/floodmodeller-api/tree/main/toolbox/model_review)| Tools to support the model review process

These tools perform standalone tasks using the Flood Modeller API and other packages. 
To run them, please read the available documentation for each tool. 



# Running a tool
API Tools can be executed from the command line or from within python code.

## From code
To run a tool from a python script, simply import the tool and then run using the `.run()` method 
(including) any input parameters. For example, you can run the Structure Log tool as follows:

``` python
from floodmodeller_api.toolbox import StructureLog

StructureLog.run(
    input_path="path/to/dat.dat",
    output_path="path/to/csv.csv",
)
```

## From the command line
You can also run API tools from the command line. Tools already included in the API toolbox can be
called from the command line simply using the tool name and prefixed with 'fmapi-'. For example to 
run the Structure Log tool from the command line you would call:

```
fmapi-structure_log --input_path "<dat file path>" --output_path "<give a file path to a csv>"
```

As well as passing the arguments in this way, you can also invoke a very simple GUI by simply passing
the argument 'gui':

```
fmapi-structure_log gui
```

# Developing Custom Tools
You can develop your own tools to integrate with the Flood Modeller Python API!

There are a few conventions you need to follow to do this.
- Add a python file or folder to one of the directories in the toolbox
- Write the tool functionality however you prefer (i.e. a single function, a class, or even a module with multiple files)
so long as there is a single entry-point for the tool
- Create a 'tool_definition' python file and define the tool using the FMTool class, passing in the tool name and description, function to be run and the function parameters.
- Finally, ensure to expose your tool to the floodmodeller_api.toolbox module by including it in the 
toolboc module `__init__.py` files

See the [example_tool.py](example_tool.py) script for an example of how to do this.

When developing your own custom tools, they will not automatically be included in the package scripts
and so will not be exposed to run as above, but a simple way to do this for custom tools is to just
include an `if __name__ == "__main__"` block in your definition file (or any python file that imports
the tool) and call the tool's `run_from_command_line()` method. This will allow you to run that python 
file directly from the command line with python and pass in any required arguments. For example, 
including something like:

``` python
# some_file.py
if __name__ == "__main__":
    SomeCustomTool().run_from_command_line()
```

and then running it with:
```
python some_file.py --some_argument "something"
```
