***********
ZZX Class
***********
Summary
--------
The ``ZZX`` class allows for rapid reading of Flood Modeller's native results format (.zzx). The class must be intiated with the full filepath to a given zzx file:

.. code:: python

    from floodmodeller_api import ZZX

    results = ZZX('path/to/results.zzx')

Reference
--------------
.. autoclass:: floodmodeller_api.ZZX
    
   .. automethod:: to_dataframe

   .. automethod:: export_to_csv

   .. automethod:: to_json

Examples
-----------
**Example 1 - Reading and exporting 1D results**

The following example shows a simple case of using the ``ZZX`` class to read a .zzx file and return the maximum results as a dataframe.

.. code:: python

    from floodmodeller_api import ZZX

    zzx = ZZX("..\\Data\\Examples\\1D\\Flow\\EVENT DATA EXAMPLE.zzx")

    zzx.to_dataframe(result_type='max')

This would return the following pandas dataframe object:

.. code:: python

             Max Link inflow  Max Left FP h  Max Right FP h  Max Left FP mode  Max Right FP mode
    Label
    resin                0.0   -9999.990234    -9999.990234               1.0                1.0
    CS26                 0.0   -9999.990234    -9999.990234               1.0                1.0
    CS25                 0.0   -9999.990234    -9999.990234               1.0                1.0
    RD25Sd               0.0   -9999.990234    -9999.990234               1.0                1.0
    CS24                 0.0   -9999.990234    -9999.990234               1.0                1.0
    FOOTBRu              0.0   -9999.990234    -9999.990234               1.0                1.0
    FOOTBRd              0.0   -9999.990234    -9999.990234               1.0                1.0
    FOOTb                0.0   -9999.990234    -9999.990234               1.0                1.0
    DS3                  0.0   -9999.990234    -9999.990234               1.0                1.0
    DS4                  0.0   -9999.990234    -9999.990234               1.0                1.0

Additional options can be specified in the ``to_dataframe()`` method to access subsets of results:

.. code:: python

   zzx.to_dataframe(result_type='max', variable='Flow', include_time=True)

             Max Link inflow  Max Link inflow Time(hrs)
    Label
    resin                0.0                        0.0
    CS26                 0.0                        0.0
    CS25                 0.0                        0.0
    RD25Sd               0.0                        0.0
    CS24                 0.0                        0.0
    FOOTBRu              0.0                        0.0
    FOOTBRd              0.0                        0.0
    FOOTb                0.0                        0.0
    DS3                  0.0                        0.0
    DS4                  0.0                        0.0

The `ZZX` class can also be used to directly access the metadata stored within the zzx file, using the ``meta`` property - a dictionary containing the following data:


**ZZX class 'meta' keys**

.. table:: 
   :align: left

   ===============  ========================  ==============
   Key              Data Type                 Description   
   ===============  ========================  ==============
   ``zzx_name``     String                    Full path to ZZX file
   ``labels``       List of strings           Array of node labels
   ``model_title``  String                    Model title including DAT file and Flood Modeller version
   ``dt``           Float                     Model timestep (s)
   ``nnodes``       Integer                   Number of model nodes 
   ``save_int``     Float                     Simulation save interval (s)
   ===============  ========================  ==============


