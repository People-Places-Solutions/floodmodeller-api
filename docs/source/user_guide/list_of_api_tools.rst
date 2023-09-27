*****************
List of API Tools
*****************

.. _tuflow_to_fm:

tuflow_to_floodmodeller
-----------------------

The tool defined in this file converts models from TUFLOW to Flood Modeller.
It is intended to be a first step in the conversion process.

Provide a path to the tcf file, a folder to store new files in, and the name of the model.
The tool will then try to convert the following components:

- Computational Area
- Topography
- Roughness
- Numerical Scheme
- Estry Model

If a component fails to convert, the tool will not crash.
Instead, it will skip that component and print the error in the log.

**Usage**

To use the Tuflow converter can use either the command line:

``tuflow_to_floodmodeller --tcf_path "<tcf file path>" --folder "<where to save new model>" --name "<name for new model>"``

Or as a gui:

``tuflow_to_floodmodeller gui``

Or you can use it from your code:

.. code:: python 

    from floodmodeller_api.toolbox import TuflowToFloodModeller

    TuflowToFloodModeller.run(
        tcf_path="path/to/tcf.tcf",
        folder="path/to/model",
        name="model_name",
    )

.. _structure_log:

structure_log
-----------------------

This tool creates an output log (.csv file) of all the conduits and structures within a DAT file.
It lists:

- Unit Name
- Unit Type
- Unit Subtype
- Comment
- Friction
- Distance (m)
- Weir Coefficient
- Culvert Inlet/Outlet Loss

**Usage**

To use this tool, you can either run it from the command line:

``structure_log --input_path "<dat file path>" --output_path "<give a file path to a csv>"``

Or as a gui:

``structure_log gui``

Or you can use it from your code:

.. code:: python 

    from floodmodeller_api.toolbox import StructureLog

    StructureLog.run(
        input_path="path/to/dat.dat",
        output_path="path/to/csv.csv",
    )

.. _raise_section_bed_levels:

raise_section_bed_levels
------------------------

.. _interactive_flow_graph:

interactive_flow_graph
----------------------