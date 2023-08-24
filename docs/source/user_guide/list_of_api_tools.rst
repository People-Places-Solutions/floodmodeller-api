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

Or you can use it from your code:

.. code:: python 

    from floodmodeller_api.toolbox import TuflowToFloodModeller

    TuflowToFloodModeller.run(
        tcf_path="path/to/tcf.tcf",
        folder="path/to/model",
        name="model_name",
    )