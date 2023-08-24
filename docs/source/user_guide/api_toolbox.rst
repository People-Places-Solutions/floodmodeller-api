************
API Toolbox
************

.. _summary:

Summary
-------

This toolbox serves as a place to store and maintain production-ready tools that integrate with the Flood Modeller Python API.

Tools will sit under the following categories: Results Analysis, Model Build, Model Conversion and Visualisation.

These tools act as standalone scripts. To run them, please read the available documentation for each tool.

.. _fmapi_toolbox_cli:

fmapi-toolbox cli
-----------------

.. _how_to_run_a_tool:

How to run a tool
-----------------
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

.. _how_edit_existing_tool:

How to edit an existing tool
----------------------------

.. _how_to_add_a_new_tool:

How to add a new tool
---------------------

You can develop your own tools to integrate with the Flood Modeller Python API.

There are a few conventions you need to follow to do this:

- Add a python file to one of the directories in the toolbox
- Within the file, define the tool as single function
- Within the same file, create a child class of FMTool, passing in the tool name and description, funciton to be run and the function parameters

See the *example_tool.py* script for an example of how to do this.

**Create the code**

**Add a definition file**

**Register it as a script**

.. _how_to_add_new_execution_method:

How to add a new execution method
---------------------------------
