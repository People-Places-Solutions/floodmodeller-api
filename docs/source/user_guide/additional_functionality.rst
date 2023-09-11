Additional Functionality
=========================

This section provides information on some additional functionality of the API that is not
specific to any single class.

Difference and equivalence methods
-----------------------------------
When working with the API, it is often useful to understand whether two instances of a class
are equal, or if not, what the differences are. In general, the API considers two instances
equal if they contain the exact same data and therefore would write the same output. Some
attributes such as the filepath do not need to be the same for them to be considered equal.

Two instances of the same class can now be tested using ``==`` to check whether they are 
equal.

.. code:: python 

    dat_a = DAT('some_network.dat')
    dat_b = DAT('another_similar_network.dat')

    if dat_a == dat_b:  # returns True/False
        print('Files are equivalent')
    else:
        print('Files not equivalent')


In addition, a detailed breakdown of any differences can be found using the ``.diff()`` 
method:

.. code:: python
    
    dat_a.diff(dat_b)  # prints a list of differences to terminal
 
Currently, the ``==`` and ``.diff()`` methods is supported for the following classes:

- DAT
- IED
- IEF
- INP
- XML2D
- All 1D River Unit classes 

File Backups
------------
The API automatically backs up any data files you load via the DAT, IED, IEF, INP and XML2D classes. The files are backed up in your OS temporary directory (see `tempfile.gettempdir()`). 
You can restore backups via the the `.file.restore()` method. Currently this restores the latest backup, but if you want to restore a specific backup then you list the backups and navigate to the file via the os file directory.

.. code:: python

    # Load the DAT
    # Automatically backs up the file if it has changes since the last backup
    dat = DAT("a_dat_file.DAT")
    # List the available backups
    backups = dat.file.list_backups()
    # Restore the latest backup to a file
    backups[0].restore(to = "restore-file.DAT")
    # Restore an older backup
    backups[6].restore(to = "restore-file.DAT")


API Toolbox
------------
You can extend the API by building custom Tools! `floodmodeller_api.toolbox.FMTool` provides a common structure for developing custom tools and automatically extends a tool with a command line and simple graphical user interface (via `tkinter`). 

To develop a custom tool and extend with `FMTool`, follow the example below.

1. Write a function to do what you need to do! You can do whatever you want here, but for now you will need to save the output to a file and pass any complex python objects (e.g. a `DAT`) as a file path.

.. code:: python

    # Import modules
    ## Modules for the function
    from pathlib import Path
    from floodmodeller_api import DAT

    ## Define the function ----------------- #
    # This function allows you to raise the minimum bed level 300mm across all sections in a DAT file (i.e siltation)
    def raise_section_bed_levels(dat_input:Path, dat_output:Path, min_level_m:float):
        dat = DAT(dat_input) # Initialise DAT class

        for name, section in dat.sections.items(): # iterate through all river sections
            df = section.data # get section data
            min_elevation = df["Y"].min() # get minimum cross section elevation
            raised_bed = min_elevation + min_level_m # define new lowest bed level
            df.loc[df["Y"] < raised_bed, "Y"] = raised_bed # Raise any levels lower than this to the new lowest level

        dat.save(dat_output) # save updates 

2. Then create a child class of the FMTool:

You need to add the class attributes for:
- `name` The name of the tool (displayed in the GUI)
- `description` A description of the tool, also displayed in the GUI
- `parameters` a list of parameters defining the parameter name (must be unique), type and other information
- `tool_function` The function that should be executed, `raise_section_bed_levels` in this example


.. code:: python

    ## Modules to create a tool
    from floodmodeller_api.toolbox import FMTool, Parameter
    ## Wrap the FMTool class ---------------- #
    class RaiseBedLevelsTool(FMTool):
        name = "Raise Bed Levels Tool"
        description = "Tool to raise bed levels of river sections in a DAT file"
        parameters = [
            Parameter(name="dat_input", dtype=str, description="Path to input DAT file", help_text="Not helpful text", required=True), 
            Parameter(name="dat_output", dtype=str, description="Path to output  DAT file", help_text="Not helpful text", required=True),
            Parameter(name="min_level_m", dtype=float,  description="Minimum bed level to raise to (in meters)", help_text="Not helpful text", required=True)
        ]
        tool_function = raise_section_bed_levels


You can then run the GUI like this:

.. code:: python

    tool = RaiseBedLevelsTool()
    tool.run_gui()

Or expose it to the command line like this:

.. code:: python
    
    if __name__ == "__main__":
        tool = RaiseBedLevelsTool()
        tool.run_from_command_line()
