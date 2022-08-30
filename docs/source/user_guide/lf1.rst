***********
LF1 Class
***********
Summary
--------
The ``LF1`` class allows for rapid reading of Flood Modeller's log file format (.lf1). The class must be intiated with the full filepath to a given lf1 file:

.. code:: python

    from floodmodeller_api import LF1

    results = LF1('path/to/log.lf1')

Reference
--------------
.. autoclass:: floodmodeller_api.LF1
    
   .. automethod:: to_dataframe

   .. automethod:: read

Examples
-----------
**Example 1 - Reading log file and exporting to dataframe**

The following example shows a simple case of using the ``LF1`` class to read a .lf1 file and return the changing parameters as a dataframe.

.. code:: python

    from floodmodeller_api import LF1

    lf1 = LF1("..\\sample_scripts\\sample_data\\ex3.lf1")

    lf1.to_dataframe()

This would return the following pandas dataframe object:

.. code:: python

        mass_error               timestep         elapsed       simulated iterations         convergence           flow        
                 0                      0               0               0       iter log(dt)        flow   level inflow outflow
    0          NaN        0 days 00:05:00 0 days 00:00:00 0 days 00:00:00        NaN     NaN         NaN     NaN    NaN     NaN
    1          NaN        0 days 00:05:00 0 days 00:00:00 0 days 00:00:00        NaN     NaN         NaN     NaN    NaN     NaN
    2         0.00 0 days 00:00:18.750000 0 days 00:00:01 0 days 00:00:00        6.0     4.6      0.0186  0.0004   3.67    2.58
    3        -0.01 0 days 00:00:37.500000 0 days 00:00:01 0 days 00:05:00        5.0     6.2      0.0086  0.0008   3.71    2.69
    4        -0.04 0 days 00:00:37.500000 0 days 00:00:01 0 days 00:10:00        3.0     6.2      0.0036  0.0003   3.75    3.04
    ..         ...                    ...             ...             ...        ...     ...         ...     ...    ...     ...
    288      -0.04        0 days 00:05:00 0 days 00:00:03 0 days 23:50:00        3.0    11.0      0.0026  0.0020  20.55   22.65
    289      -0.03        0 days 00:05:00 0 days 00:00:03 0 days 23:55:00        3.0    11.0      0.0027  0.0020  19.79   21.86
    290      -0.03        0 days 00:05:00 0 days 00:00:03 1 days 00:00:00        3.0    11.0      0.0028  0.0020  19.04   21.06
    291        NaN        0 days 00:05:00 0 days 00:00:03 1 days 00:00:00        NaN     NaN         NaN     NaN    NaN     NaN
    292        NaN        0 days 00:05:00 0 days 00:00:03 1 days 00:00:00        3.0    11.0      0.0028  0.0020    NaN     NaN

**Example 2 - Reading log file and printing dictionary**

The `LF1` class can also be used to directly access the fixed data stored within the lf1 file, using the ``info`` property.

.. code:: python

    from floodmodeller_api import LF1

    lf1 = LF1("..\\sample_scripts\\sample_data\\ex3.lf1")

    print(lf1.info)

This prints the following dictionary:

.. code:: python
    {'version': '5.0.0.7752', 'qtol': 0.01, 'htol': 0.01, 'start_time': datetime.timedelta(0), 'end_time': datetime.timedelta(days=1), 'ran_at': datetime.datetime(2021, 9, 8, 12, 18, 21), 'max_itr': 11.0, 'min_itr': 3.0, 'progress': 100.0, 'EFT': datetime.time(12, 18, 24), 'ETR': datetime.timedelta(0), 'simulation_time_elapsed': datetime.timedelta(seconds=3), 'number_of_unconverged_timesteps': 0.0, 'proporion_of_simulation_unconverged': 0.0, 'mass_balance_calculated_every': datetime.timedelta(seconds=300), 'initial_volume': 39596.8, 'final_volume': 53229.4, 'total_lat_link_outflow': 0.0, 'max_system_volume': 270549.0, 'max_volume_increase': 230952.0, 'max_boundary_inflow': 129.956, 'net_volume_increase': 13632.6, 'net_inflow_volume': 13709.5, 'volume_discrepancy': 76.8984, 'mass_balance_error': -0.03, 'mass_balance_error_2': -0.0}

