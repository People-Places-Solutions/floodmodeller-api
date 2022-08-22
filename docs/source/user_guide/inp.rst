INP Class
=====================================================
Summary
--------
The ``INP`` class is used to read and update Flood Modeller's inp file format that is 
associated with 1D Urban models. The class is initiated with the full filepath of an INP 
file to load an existing drainage network. 

.. attention::
   
   The API functionality for Urban 1D INP files is currently in development and should be 
   treated as experimental.
     
   The API currently only supports reading/writing of a limited number of unit types. 
   Furthermore, the API does not yet support adding/deleting units. Support of additional 
   unit types, as well as functionality to create and build networks will be implemented 
   in a future release.
   
.. code:: python

    from floodmodeller_api import INP

    inp = INP('path/to/inpfile.inp') # Loads existing INP file into memory

Once you have initialised a INP class, the supported units can be accessed via the attributes: 

-  ``.junctions`` (see: :ref:`Junction units <junction_units_urban>`)
-  ``.raingauges`` (see: :ref:`Raingauge units <raingauge_units_urban>`)
-  ``.conduits`` (see: :ref:`Conduit units <conduit_units_urban>`)
-  ``.outfalls`` (see: :ref:`Outfall units <outfall_units_urban>`)
-  ``.losses`` (see: :ref:`Loss units <loss_units_urban>`)
-  ``.xsections`` (see: :ref:`XSection units <xsection_units_urban>`)

In each, the individual units of each type are stored in a dictionary of unit names and unit classes. Only units which are supported in the API will be accesible via these attributes, 
all of which can be found in the :doc:`Individual Urban 1D Unit Classes <urban1d_units>` section.

.. code:: python 

    # Print string representation of all units.
    print(inp.junctions)
    print(inp.raingauges)

Each individual unit class is somewhat unique in how they can be worked with in python. 
For each unit, the associated data can be accessed and edited via the unit's class attributes.  
For example, for a ``JUNCTION`` the the invert elevation can be accessed via the ``.elevation`` attribute: 

.. code:: python

    print(inp.junctions['MC0918'].elevation) # print the invert elevation for junction 'MC0918'
    >>> 3.28

    inp.junctions['MC0918'].elevation = 5 # Update the invert elevation to 5m

Although it is possible to rename units by passing a new name into the ``.name`` attribute, 
it is recommended to avoid this as it may cause label issues within the network. Currently the 
INP class only allows for editing existing units, however functionality to add/remove sections
will be included in a future release. For full documentation on the available unit classes, 
please refer to the :doc:`Individual Urban 1D Unit Classes <urban1d_units>` section.

In addition to the units, the general options for the INP file can be accessed through the ``.options`` attribute. This contains a dictionary of all the general 
INP settings and can be edited by assigning them new values. 

.. code:: python

    inp.general_parameters # Access dictionary of general INP parameters
    >>> {
            "flow_units": "CFS",
            "infiltration": "HORTON",
            "flow_routing": "KINWAVE",
            "link_offsets": "DEPTH",
            "force_main_equation": "H-W",
            "ignore_rainfall": None,
            "ignore_snowmelt": None,
            "ignore_groundwater": None,
            "ignore_rdii": None,
            "ignore_routing": None,
            "ignore_quality": None,
            "allow_ponding": "NO",
            "skip_steady_state": "NO",
            "sys_flow_tol": "5",
            "lat_flow_tol": "5",
            "start_date": "09/13/2014",
            "start_time": "00:00:00",
            "end_date": "09/15/2014",
            "end_time": "00:00:00",
            "report_start_date": "09/13/2014",
            "report_start_time": "00:00:00",
            "sweep_start": "01/01",
            "sweep_end": "12/31",
            "dry_days": "0",
            "report_step": "00:15:00",
            "wet_step": "00:05:00",
            "dry_step": "00:05:00",
            "routing_step": "0:00:30",
            "lengthening_step": "0",
            "variable_step": "0.75",
            "minimum_step": "0.5",
            "inertial_damping": "PARTIAL",
            "normal_flow_limited": "BOTH",
            "min_surfarea": "12.557",
            "min_slope": "0",
            "max_trials": "8",
            "head_tolerance": "0.005",
            "threads": "1",
            "tempdir": None,
        }

Reference
--------------
.. autoclass:: floodmodeller_api.INP
    
   .. automethod:: update

   .. automethod:: save

   .. automethod:: diff

Examples
-----------
**Example 1 - Increase non-zero initial depths for all junctions** 

In this example, the the initial depth of all junctions is to be increased by 200m only where the exiting initial depth is non-zero.  The updated INP file is saved to a new
location rather than updating the original file.

.. code:: python

    # Import modules
    from floodmodeller_api import INP

    # Initialise INP class
    inp = INP(
        r"C:\Projects\FloodModellerAPI\Development\Example Data\Oldsmar_50YR_1DAY.inp"
    )

    # Iterate through all junction units
    for name, junction in inp.junctions.items():

        # Add 200mm to initial depth if not equal to 0
        if junction.initial_depth != 0:
            junction.initial_depth += 0.2

    # Save update inp to new location
    inp.save(
        r"C:\Projects\FloodModellerAPI\Development\Example Data\inpfile_increased_initial_depth.inp"
    )  # Save to new location


