****************
IED Class
****************
Summary
--------
The ``IED`` class is used to read, write and update Flood Modeller's ied file format. The class can be initiated with the full filepath of an ied file to load 
an existing ied, or with no path to create a new ied file in memory.

.. code:: python

    from floodmodeller_api import IED

    ied = IED('path/to/event.ied') # Loads existing IED into memory 
    new_ied = IED() # Used to create new 'blank' IEF 

Once you have initialised an IED class, the individual boundary units will be accessible as a dictionary in the ``.boundaries`` attribute:

.. code:: python

    # Print string representation of all boundary units.
    print(ied.boundaries) 

    # Print each individual boundary unit name
    for name, unit in ied.boundaries.items():
        print (name) 

.. tip::
   If present, other units are accessible in the ``.sections``, ``.conduits``, ``.structures`` and ``.losses`` attributes respectively - see :doc:`DAT <dat>` section for more information 
   on working with these unit types.

Each boundary unit class will typically contain all parameters as class attributes, plus the main data table saved in ``.data`` as a ``pandas.Series()``. These can all be updated 
directly, and will be reflected in the IED file after calling ``IED.update()`` or ``IED.save()``. For example, to access the flow-time data for a ``QTBDY`` unit you could run:

.. code:: python

    # Access the boundary units available in IED class object 'ied', with the name 'inflow_1'
    ied.boundaries['inflow_1']
    >>> <floodmodeller_api Unit Class: QTBDY(name=qflow_new)>

    type(ied.boundaries['inflow_1']) # You can test the type to ensure it is a QTBDY unit
    >>> <_class 'units.QTBDY'>

    ied.boundaries['inflow_1'].data # Flow data can be accessed via the 'data' attribute
    >>> Time  
        0.0   0.0
        1.0   0.5
        2.0   2.0
        3.0   4.5
        4.0   8.0
        5.0  12.5
        6.0  18.0
        7.0  24.5
        8.0  32.0
        9.0  40.5
        Name: Flow, Length: 10, dtype: float64

If the name of a unit is updated using the ``.name`` attribute, when the class is next updated the unit will then only be accessible using the updated name within the ``boundaries`` 
dictionary object.

Individual units can be deleted entirely by calling:

.. code:: python

    del ied.boundaries['inflow_1'] # Specificy name of unit to delete

New units can also be created and/or added into an IED by simply adding a new element to the ``boundaries`` dictionary using the name as the key and a valid unit class as the element. 
For example to add a brand new blank ``HTBDY`` into an ied, you could run:

.. code:: python

    new_htbdy = HTBDY(name='ds_bdy') # Initialises a new HTBDY unit with name 'ds_bdy'
    ied.boundaries['ds_bdy'] = new_htbdy # Add new element to boundaries dictionary

.. tip::
   Full details on all the various boundary unit classes can be found in the :ref:`Boundary units <boundary_units>` section.

You can get all of the units currently unsupported by the api that have been read in from the ied file:

.. code:: python

    ied._unsupported
    >>> { 
            <floodmodeller_api Unit Class: FSSR16BDY(name=resin, type=False)>
        }

Or if you want to get both supported & unsupported units:

.. code:: python
    
    ied._all_units
    >>> { 
            <floodmodeller_api Unit Class: FSSR16BDY(name=resin, type=False)>,
            <floodmodeller_api Unit Class: QTBDY(name=CS26)>,
            <floodmodeller_api Unit Class: QHBDY(name=DS4)>
        }

Reference
--------------
.. autoclass:: floodmodeller_api.IED
    
   .. automethod:: update

   .. automethod:: save

   .. automethod:: diff

   .. automethod:: to_json

   .. automethod:: from_json

Examples
-----------

**Example 1 - Altering the flow hydrograph in all QTBDYs**

The following example demonstrates how the ``IED`` class could be used to edit the flow hydrograph within all ``QTBDY`` units within an IED file.

.. code:: python

    # Import modules
    from floodmodeller_api import IED
    from floodmodeller_api.units import QTBDY # importing the QTBDY Unit class to enable checking unit type

    # Read IED file into new IED Class object
    ied = IED('path/to/event.ied')

    # Define custom function to alter the flow hydrograph to have a minimum flow of 30% of peak flow ONLY on the falling limb
    def update_hydrograph (qtbdy_unit):
        hydrograph = qtbdy_unit.data # Get hydrograph from qtbdy unit
        peak_flow = hydrograph.max() # Get peak flow value
        peak_flow_idx = hydrograph.loc[hydrograph == peak_flow].index # Get index of peak flow
        for time, flow in hydrograph.items(): # Iterate through hydrograph series
            if time > peak_flow_idx: # For only flows after peak flow i.e. falling limb
                if flow < peak_flow * 0.3: # If the flow is less than 30% of the peak
                    hydrograph.loc[time] = peak_flow * 0.3 # Maintain minimum flow of 30% of peak for remainder of hydrograph

    # Iterate through all QTBDY units
    for name, unit in ied.boundaries.items():
        if type(unit) == QTBDY: # check if unit is a QTBDY type
            update_hydrograph(unit) # Call the custom function defined above to alter hydrograph

    ied.update() # Update the changes in the IED file

**Example 2 - Adding a new QHBDY from csv data**

This example demonstrates how a new ``QHBDY`` unit could be created from a csv containing flow-head relationship and added into an existing IED file. In this example the csv data is in the following format:

.. code::

    flow,   head
    0.0,    0.000000
    0.5,    4.000000
    1.0,    6.000000
    1.5,    7.333333
    2.0,    8.333333
    ...
    13.0,   15.417679
    13.5,   15.565827
    14.0,   15.708684
    14.5,   15.846615
    15.0,   15.979949

Code:

.. code:: python

    # Import modules
    from floodmodeller_api import IED
    from floodmodeller_api.units import QHBDY # importing the QHBDY Unit class
    import pandas as pd

    # Read in QH csv
    qh_data = pd.read_csv('path\to\data.csv', index_col=0).squeeze() # .squeeze()) to read in as a Series object

    # Create new QHBDY Unit
    new_qhbdy = QHBDY(name='DS_1', data=qh_data, comment='New downstream boundary') # Additional info such as unit name and comment are added. 

    # Read existing IED file
    ied = IED('path/to/event.ied')

    # Add in the new QHBDY
    ied.boundaries['DS_1'] = new_qhbdy # Added as new key in 'boundaries' dictionary with matching name

    # Update the existing IED file
    ied.update()



