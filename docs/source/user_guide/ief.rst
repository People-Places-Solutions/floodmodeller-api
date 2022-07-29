**********
IEF Class
**********
Summary
---------
The ``IEF`` class is used to read, write and update Flood Modeller's ief file format. 
The class can be initiated with the full filepath of an ief file to load an existing ief, 
or with no path to create a new ief file in memory.

.. code:: python

    from floodmodeller_api import IEF

    ief = IEF('path/to/simulation.ief') # Loads existing IEF into memory 
    new_ief = IEF() # Used to create new 'blank' IEF 

All standard IEF settings can be changed by the user by simply updating the class property 
with the same name. For example to set the model title, simply type: 

.. code:: python
    
    ief.title = "My New Title"

.. warning::
   Any changes made to the IEF class object are only made to the object itself and do not change the source IEF file until the
   ``.update()`` method is called. Alternatively if the ``.save()`` method is called then the changes are saved to a new file (based on the given
   path) and the original source IEF remains unchanged

Class properties can be updated in this fashion for existing IEF settings as well as to 
add new settings. To remove a particular setting from the IEF simply delete the propery 
object, for example to remove 'LINKFLOW' simple type: 

.. code:: python

    del ief.linkflow

.. note:: 
   IEF properties can be accessed using any casing (e.g. ``ief.results`` is equivalent to
   ``ief.Results``) therefore any scripts using the IEF class can be implemented using 
   typical python style with lowercase properties, whilst retaining the casing in the original
   file. 

Class properties can also be managed using python's built-in ``getattr()``, ``setattr()`` and ``delattr()`` functions, using these methods is recommended for more 
complex updates such as updating settings from a dictionary of values, but is required for certain IEF settings which are prefixed with a number such as '2DFLOW' 
since these are not valid python variables. An example of updating the '2DFLOW' setting in this way is:

.. code:: python

    setattr(ief, '2DFLOW', 1) # Sets the IEF's '2DFLOW' setting to 1

IEF files can also be simulated directly by calling the ``.simulate()`` method on an active IEF class object. This method assumes that Flood Modeller is installed
at the default location ('C:\\Program Files\\Flood Modeller\\bin'). An optional argument ``'method'`` is used to control whether the python code should pause until the 
simulation has completed, or to return the simulation as a ``subprocess.Popen()`` instance and continue code execution. By default, the 'WAIT' method is used to provide
a simple way to know when the simulation has completed. Using the option to return the process as an object would mostly be used for more complex scripts where you are 
wanting to have more control over checking simulation progress and performing any tasks whilst the simulation is running. Subprocess is a package included in the Python
Standard Library which allows for spawning new processes and handling their input and output pipes. More information on working with ``subprocess.Popen()`` can be found
`here <https://docs.python.org/3/library/subprocess.html#subprocess.Popen>`_.

Reference
----------
.. autoclass:: floodmodeller_api.IEF
    
   .. automethod:: update

   .. automethod:: save

   .. automethod:: simulate

   .. automethod:: get_results

Examples
-----------
**Example 1 - Update all IEFs in a folder to point to a new DAT file**

The following example shows how the `IEF` class could be used to iteratively update all IEF files in a folder to point to a new DAT file.

.. code:: python
    
    # Import modules
    from glob import glob
    from floodmodeller_api import IEF

    # Point to folder of interest
    folder = r'C:\FloodModeller_ExampleData\Examples\1D\Flow'

    # Get list of IEF files using glob function
    ief_files = glob(folder + '\*.ief')

    for ief_path in ief_files:
        ief = IEF(ief_path) # Initiate IEF Class Object
        ief.Datafile = r'..\NEW_RIVER_001.DAT' # Set 'Datafile' setting to new DAT file location
        ief.update() # Update the IEF file

**Example 2 - Create new set of IEFs versions based on previous IEF files**

The following example shows how the `IEF` class could be used to create a new set of IEF files with the title, results and filepath updated to 'v2' 

.. code:: python

    # Import modules
    from glob import glob
    from floodmodeller_api import IEF

    # Point to folder of interest
    folder = r'C:\FloodModeller_ExampleData\Examples\1D\Flow'

    # Get list of IEF files using glob function
    ief_files = glob(folder + '\*.ief')

    for ief_path in ief_files:
        ief_name = os.path.basename(ief_path) # get existing filename
        new_ief_name = ief_name.replace('.ief', '_v2.ief') # update filename with 'v2' appended
        new_ief_path = os.path.join(folder, new_ief_name) # get updated filepath

        ief = IEF(ief_path) # Initiate IEF Class Object
        ief.Title += '_v2' # Update title
        if 'Results' in dir(ief):
            ief.Results += '_v2' # If Results setting already exists, append v2
        else:
            ief.Results = 'v2' # If no results yet specified, set results to v2

        ief.save(new_ief_path) # Save updated IEF files to the new filepath

**Example 3 - Simulate an IEF and read the results directly**

The following example shows how the `IEF` class could be used to set a simulation going and then access the
1D results directly once it has completed.

.. code:: python

    # Import modules
    from floodmodeller_api import IEF

    ief_file = r'path\to\simualtion.ief'

    # Instantiate IEF Class object 
    ief = IEF(ief_file)

    # Simulate IEF (the default is for python to wait until simulation is complete)
    ief.simulate()

    # Access results directly into ZZN class object
    zzn = ief.get_results()

    # Get dataframe from results
    my_results = zzn.to_dataframe()

