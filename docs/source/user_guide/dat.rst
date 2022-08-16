DAT Class
=====================================================
Summary
--------
The ``DAT`` class is used to read and update Flood Modeller's dat file format. The class is initiated with the full filepath of a DAT file to load an existing network. 

.. note::
   Currently the API only supports editing existing DAT networks and units. Unlike the IED class which allows for creating new IEDs and adding/deleting units. Functionality 
   to create and build networks will be implemented in a future release.

.. code:: python

    from floodmodeller_api import DAT

    dat = DAT('path/to/datafile.dat') # Loads existing DAT file into memory

Once you have initialised a DAT class, the sections, structures, and boundary units can be accessed via the attributes:

-  ``.sections`` (see: :ref:`Section units <section_units>`)
-  ``.conduits`` (see: :ref:`Conduit units <conduit_units>`)
-  ``.structures`` (see: :ref:`Structure units <structure_units>`)
-  ``.boundaries`` (see: :ref:`Boundary units <boundary_units>`)
-  ``.losses`` (see: :ref:`Loss units <loss_units>`)

In each, the units are stored in a dictionary of unit names and unit classes. Only units which are supported in the API will be accesible via these attributes, all of which can be 
found in the :doc:`Individual Unit Classes <units>` section.

.. code:: python 

    # Print string representation of all units.
    print(dat.sections)
    print(dat.conduits)
    print(dat.structures)
    print(dat.boundaries)
    print(dat.losses)

Each individual unit class is somewhat unique in how they can be worked with in python, but generally most unit classes will have a ``.name``, ``.comment`` and ``.data`` attribute. 
For example, a ``RIVER`` unit class contains the full section data as a dataframe:

.. code:: python
        
    dat.sections['S5'].data # Accessing the section data for river section 'S5'

    >>> 
        X     Y  Mannings n  Panel  RPL Marker  Easting  Northing Deactivation  SP. Marker
    0  -10.0  10.0        0.03  False  0.0             0.0       0.0                        0
    1   -9.0   9.0        0.03  False  0.0             0.0       0.0                        0
    2   -8.0   8.0        0.03  False  0.0             0.0       0.0                        0
    3   -7.0   7.0        0.03  False  0.0             0.0       0.0                        0
    4   -6.0   6.0        0.03  False  0.0             0.0       0.0                        0
    5   -5.0   5.0        0.03  False  0.0             0.0       0.0                        0
    6   -4.0   4.0        0.03  False  0.0             0.0       0.0                        0
    7   -3.0   3.3        0.03  False  0.0             0.0       0.0                        0
    8   -2.0   3.3        0.03  False  0.0             0.0       0.0                        0
    9   -1.0   3.3        0.03  False  0.0             0.0       0.0                        0
    10   0.0   3.3        0.03  False  0.0             0.0       0.0                        0
    11   1.0   3.3        0.03  False  0.0             0.0       0.0                        0
    12   2.0   3.3        0.03  False  0.0             0.0       0.0                        0
    13   3.0   3.3        0.03  False  0.0             0.0       0.0                        0
    14   4.0   4.0        0.03  False  0.0             0.0       0.0                        0
    15   5.0   5.0        0.03  False  0.0             0.0       0.0                        0
    16   6.0   6.0        0.03  False  0.0             0.0       0.0                        0
    17   7.0   7.0        0.03  False  0.0             0.0       0.0                        0
    18   8.0   8.0        0.03  False  0.0             0.0       0.0                        0
    19   9.0   9.0        0.03  False  0.0             0.0       0.0                        0
    20  10.0  10.0        0.03  False  0.0             0.0       0.0                        0

All other associated data can be accessed and edited for a ``RIVER`` unit class via class attributes, for example the 'distance to next section' can be accessed using the 
``.dist_to_next`` attribute:

.. code:: python

    print(dat.sections['S5'].dist_to_next) # print the distance to next section for river section 'S5'
    >>> 105.0

    dat.sections['S5'].dist_to_next = 150.0 # Update the distance to next section to 150m

Although it is possible to rename units by passing a new name into the ``.name`` attribute, it is recommended to avoid this as it may cause label issues within the network. 
Currently the DAT class only allows for editing existing units, however functionality to add/remove sections will be included in a future release. For full documentation on 
the available unit classes, please refer to the :doc:`Individual Unit Classes <units>` section.

In addition to the units, the general parameters for the DAT file can be accessed through the ``.general_parameters`` attribute. This contains a dictionary of all the general 
DAT settings and can be edited by assigning them new values. 

.. warning:: 
   Only change values in the general parameters which you are sure can be edited. For example, 'Node Count' 
   should be treated as read-only

.. code:: python

    dat.general_parameters # Access dictionary of general DAT parameters
    >>> {
            "Node Count": 14,
            "Lower Froude": 0.75,
            "Upper Froude": 0.9,
            "Min Depth": 0.1,
            "Convergence Direct": 0.001,
            "Units": "DEFAULT",
            "Water Temperature": 10.0,
            "Convergence Flow": 0.01,
            "Convergence Head": 0.01,
            "Mathematical Damping": 0.7,
            "Pivotal Choice": 0.1,
            "Under-relaxation": 0.7,
            "Matrix Dummy": 0.0,
            "RAD File": ""
        }

Reference
--------------
.. autoclass:: floodmodeller_api.DAT
    
   .. automethod:: update

   .. automethod:: save

   .. automethod:: diff

Examples
-----------
**Example 1 - Adding 300mm siltation to all river sections** 

In this example, the cross section data for individual river sections needs to be edited to add 300mm to the lowest bed level and make this the minimum bed level across the 
entire section. This is a simple method to quickly represent siltation in the channel. The updated DAT file is saved to a new location rather than updating the original file.

.. code:: python

    # Import modules
    from floodmodeller_api import DAT

    # Initialise DAT class
    dat = DAT('path/to/datafile.dat')

    # Iterate through all river sections
    for name, section in dat.sections.items():
        df = section.data # get section data
        min_elevation = df['Y'].min() # Get minimum bed level across section
        raised_bed = min_elevation + 0.3 # Define new minimum bed level by adding 0.3m
        df['Y'].loc[df['Y'] < raised_bed] = raised_bed # Update any bed levels which are less than the new min bed level

    dat.save('path/to/datafile_300mm_siltation.dat') # Save to new location


