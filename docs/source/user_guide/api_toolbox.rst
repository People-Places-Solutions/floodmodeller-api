************
API Toolbox
************

.. _summary:

Summary
-------

This toolbox serves as a place to store and maintain production-ready tools that integrate with the Flood Modeller Python API.

Tools will sit under the following categories: Results Analysis, Model Build, Model Conversion and Visualisation.

These tools act as standalone scripts. To run them, please read the available documentation for each tool.

.. _fmapi_toolbox:

fmapi-toolbox
-------------

A tool to use in the command line to interact with all the API toolbox scripts.

You can use these command line arguements:

- *-l* or *-list* : list all toolbox scripts installed
- *-ld* or *-list-detailed* : list all toolbox scripts installed including usage
- *-r* or *-register* : register a new tool to the fmapi-toolbox

.. _run_a_tool:

Run a tool
----------

Tools can be run from the command line or from code: 

.. note::   
    The following are *tuflow_to_floodmodeller* examples, each tool will be slightly different

**From the command line**

``tuflow_to_floodmodeller --tcf_path "<tcf file path>" --folder "<where to save new model>" --name "<name for new model>"``

**From code**

.. code:: python 

    from floodmodeller_api.toolbox import TuflowToFloodModeller

    TuflowToFloodModeller.run(
        tcf_path="path/to/tcf.tcf",
        folder="path/to/model",
        name="model_name",
    )

.. _edit_existing_tool:

Edit an existing tool
---------------------

You can edit previously existing tools for the Flood Modeller API.

Go to the scripts folder and select the tool you want to edit, then change what you want to.

.. _add_a_new_tool:

Add a new tool
--------------

You can develop your own tools to integrate with the Flood Modeller Python API.

There are a few conventions you need to follow to do this:

- Add a python file to one of the directories in the toolbox, depending on the category of the tool
- Within the file, define the tool as a single function (add a definition file)
- Within the same file, create a child class of FMTool, passing in the tool name and description, funciton to be run and the function parameters
- Register the file as a script 

See the *example_tool.py* script in the toolbox for an example of how to do this.

.. _add_new_execution_method:

Add a new execution method
--------------------------

You can add command-line execution for a tool by having its *.py* and *.bat* scripts in the *scripts* folder.

.. code:: python

    example.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    from floodmodeller_api.toolbox import Example
    Example().run_from_command_line()

.. code:: console

    example.bat
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @echo off
    python "%~dp0\example.py" %*