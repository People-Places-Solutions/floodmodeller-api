**********
IEF Class
**********
Summary
---------
The :class:`~floodmodeller_api.IEF` class is used to read, write and update Flood Modeller's ief file format. 
The class can be initiated with the full filepath of an ief file to load an existing ief, 
or with no path to create a new ief file in memory.

.. ipython:: python

    from floodmodeller_api import IEF;

    ief = IEF("network.ief") # Loads existing IEF into memory 
    new_ief = IEF(); # Used to create new 'blank' IEF 
    new_ief

All standard IEF settings can be changed by the user by simply updating the class property 
with the same name. For example to set the model title, simply type: 

.. ipython:: python
    
    ief.title = "My New Title";
    ief.title

.. warning::
   Any changes made to the IEF class object are only made to the object itself and do not change the
   source IEF file until the :meth:`~floodmodeller_api.IEF.update` method is called. Alternatively 
   if the :meth:`~floodmodeller_api.IEF.save` method is called then the changes are saved to a new 
   file (based on the given path) and the original source IEF remains unchanged

Class properties can be updated in this fashion for existing IEF settings as well as to 
add new settings. To remove a particular setting from the IEF simply delete the property 
object, for example to remove 'LINKFLOW' simple type: 

.. code:: python

    del ief.linkflow

.. note:: 
   IEF properties can be accessed using any casing (e.g. ``ief.results`` is equivalent to
   ``ief.Results``) therefore any scripts using the IEF class can be implemented using 
   typical python style with lowercase properties, whilst retaining the casing in the original
   file. 

Class properties can also be managed using python's built-in ``getattr()``, ``setattr()`` and 
``delattr()`` functions, using these methods is recommended for more complex updates such as 
updating settings from a dictionary of values, but is required for certain IEF settings which are 
prefixed with a number such as '2DFLOW' since these are not valid python variables. An example of
updating the '2DFLOW' setting in this way is:

.. code:: python

    setattr(ief, '2DFLOW', 1) # Sets the IEF's '2DFLOW' setting to 1

IEF files can also be simulated directly by calling the :meth:`~floodmodeller_api.IEF.simulate()` 
method on an active IEF class object. This method assumes that Flood Modeller is installedat the default location 
('C:\\Program Files\\Flood Modeller\\bin'). An optional argument ``'method'`` is used to control 
whether the python code should pause until the simulation has completed, or to return the simulation
as a ``subprocess.Popen()`` instance and continue code execution. By default, the 'WAIT' method is 
used to providea simple way to know when the simulation has completed. Using the option to return 
the process as an object would mostly be used for more complex scripts where you are wanting to have
more control over checking simulation progress and performing any tasks whilst the simulation is 
running. Subprocess is a package included in the Python Standard Library which allows for spawning 
new processes and handling their input and output pipes. More information on working with 
``subprocess.Popen()`` can be found
`here <https://docs.python.org/3/library/subprocess.html#subprocess.Popen>`_.

Working with Event Data attributes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An IEF file can have any number of 'EventData' attributes which point to the location of
IED files. In the IEF class these are all contained within the ``.eventdata`` attribute
as a dictionary. This allows for each event data to have an associated title which is defined in
the IEF file as a comment before the event data attribute. The dictionary keys represent
the titles, and the values represent the event data paths. An example would look like this:
    
.. ipython:: python 

    ief = IEF();
    ief.eventdata = {
        'MainInflow' : 'Q100.IED',
        'TribInflow' : 'Q100_trib.IED',
        'TidalBoundary' : 'T100_DSBDY.IED'
    };
  

This would then write out the following lines in the IEF file:

.. ipython:: python

    print(ief._write())

When editing event data attibutes, they can simply be edited in the same way as a dictionary. 
For example, deleting keys using ``del``, adding new keys and editing existing ones.

.. warning::
    The ``.eventdata`` attribute has been changed to use a dictionary as of version 0.4.1 of 
    the API. Previously in v0.4.0 ``.eventdata`` would return a list instead, without support
    for reading/editing the event data titles. This introduces a change which is incompatible 
    with previous versions of the API in how event data in IEF files is handled. Any existing
    code that treats eventdata as a list will need to be updated in order to run this version.

.. _flowtimeprofile_section:

Flow Time Profile data
^^^^^^^^^^^^^^^^^^^^^^^^

.. versionadded:: 0.5.0
    

In addition to using the 'EventData' attributes to define boundary conditions for a simulation, 
inflows can also be defined using any number of 'flowtimeprofile' attributes in an IEF file. These
typically look something like this in an IEF file:

.. code:: ini
    
    [Flow Time Profiles]
    NoOfFlowTimeProfiles = 2
    NoOfFlowTimeSeries = 2
    FlowTimeProfile0 = SEV19005,19,23,..\..\associated_data\Baseline unchecked.csv,hplus,100 - 11 - 2020 Upper,
    FlowTimeProfile1 = randomInflow,9,23,..\..\associated_data\Baseline unchecked.csv,hplus,100 - 11 - Reconciled Baseline,

These flow time profiles are typically generating via the Flood Modeller UI, and have a range of
different formats that can be used. For more information on how these are set up and used in 
Flood Modeller, go to 
`how-to-use-flow-time-series-datafiles <https://help.floodmodeller.com/docs/how-to-use-flow-time-series-datafiles>`_.

With the Flood Modeller API we can also access this data in a helpful way by using the 
``.flowtimeprofiles`` attribute on an IEF instance, which returns a list of :class:`~floodmodeller_api.ief.FlowTimeProfile` objects.

.. ipython:: python

    ief = IEF("7082.ief"); # IEF file containing flow time profile data
    ief.flowtimeprofiles

Each :class:`~floodmodeller_api.ief.FlowTimeProfile` can be used to access the various components that make up a flow time 
profile:

.. ipython:: python

    profile = ief.flowtimeprofiles[0];  # Access the first flow time profile
    profile.labels
    profile.csv_filepath

As with any other attribute these can all be modified and saved to the ief:

.. ipython:: python

    profile.labels.append("new_lbl");  # Adding a new label to include to the first flowtimeprofile
    profile.columns.append(10);  # Adding the relevant additional column
    profile.csv_filepath = "../some_new_flow_data.csv";  # Changing the csv filepath

    # Take a look at the resultant IEF
    print(ief._write())

We can also create new flow time profiles to add to an ief:

.. ipython:: python

    from floodmodeller_api.ief import FlowTimeProfile;
    new_profile = FlowTimeProfile(
        labels=["label1", "label2"],
        columns=[5, 6],
        start_row=4,
        csv_filepath="fmfile.csv",
        file_type="fm2",
        profile="T=100",
        comment="MultiEvent&Nodes",
        ief_filepath="../projects",
    );
    ief.flowtimeprofiles.append(new_profile);

    print(ief._write())

Reference
----------
.. autoclass:: floodmodeller_api.IEF
    
   .. automethod:: update

   .. automethod:: save

   .. automethod:: simulate

   .. automethod:: get_results

   .. automethod:: get_log

   .. automethod:: diff

   .. automethod:: to_json

   .. automethod:: from_json

.. autoclass:: floodmodeller_api.ief.FlowTimeProfile

Examples
-----------
**Example 1 - Update all IEFs in a folder to point to a new DAT file**

The following example shows how the `IEF` class could be used to iteratively update all IEF files in 
a folder to point to a new DAT file.

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
        ief.datafile = r'..\NEW_RIVER_001.DAT' # Set 'Datafile' setting to new DAT file location
        ief.update() # Update the IEF file

**Example 2 - Create new set of IEFs versions based on previous IEF files**

The following example shows how the `IEF` class could be used to create a new set of IEF files with 
the title, results and filepath updated to 'v2' 

.. code:: python

    # Import modules
    import od
    from glob import glob
    from floodmodeller_api import IEF

    # Point to folder of interest
    folder = r'C:\FloodModeller_ExampleData\Examples\1D\Flow'

    # Get list of IEF files using glob function
    ief_files = glob(folder + '\*.ief')

    for ief_path in ief_files:
        ief_name = os.path.basename(ief_path) # get existing filename
        new_ief_name = ief_name.replace('.ief', '_v2.ief') # update filename with 'v2' appended
        new_ief_path = Path(folder, new_ief_name) # get updated filepath

        ief = IEF(ief_path) # Initiate IEF Class Object
        ief.title += '_v2' # Update title
        try:
            ief.results += '_v2' # If Results setting already exists, append v2
        except AttributeError:
            ief.results = 'v2' # If no results yet specified, set results to v2

        ief.save(new_ief_path) # Save updated IEF files to the new filepath

**Example 3 - Simulate an IEF and read the results directly**

The following example shows how the `IEF` class could be used to set a simulation going and then 
access the 1D results directly once it has completed.

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

**Example 4 - Simulate an IEF and read the log directly**

The following example shows how the `IEF` class could be used to set a simulation going and then 
access the log file directly once it has completed.

.. code:: python

    # Import modules
    from floodmodeller_api import IEF

    ief_file = r'path\to\simualtion.ief'

    # Instantiate IEF Class object 
    ief = IEF(ief_file)

    # Simulate IEF (the default is for python to wait until simulation is complete)
    ief.simulate()

    # Access results directly into LF1 class object
    lf1 = ief.get_log()

    # Get dataframe from log file
    my_log = lf1.to_dataframe()

