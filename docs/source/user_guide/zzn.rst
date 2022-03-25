***********
ZZN Class
***********
Summary
--------
The ``ZZN`` class allows for rapid reading of Flood Modeller's native results format (.zzn). The class must be intiated with the full filepath to a given zzn file:

.. code:: python

    from floodmodeller_api import ZZN

    results = ZZN('path/to/results.zzn')

Reference
--------------
.. autoclass:: floodmodeller_api.ZZN
    
   .. automethod:: to_dataframe

   .. automethod:: to_dict_of_dataframes

   .. automethod:: export_to_csv

Examples
-----------
**Example 1 - Reading and exporting 1D results**

The following example shows a simple case of using the ``ZZN`` class to read a .zzn file and return the maximum results as a dataframe.

.. code:: python

    from floodmodeller_api import ZZN

    zzn = ZZN("..\\Data\\Examples\\1D\\Flow\\EVENT DATA EXAMPLE.zzn")

    zzn.to_dataframe(result_type='max')

This would return the following pandas dataframe object:

.. code:: python

                Max Flow  Max Stage  Max Froude  Max Velocity   Max Mode  Max State
    Node Label
    S1          57.537834   6.530089    0.238329      1.348901  16.849001        0.0
    CC10        57.533329   6.501225    0.241019      1.361004  16.761000        0.0
    S3          57.529274   6.471688    0.243707      1.373160  16.671000        0.0
    S4          57.525696   6.441376    0.246524      1.385859  16.580000        0.0
    S5          57.522621   6.410248    0.249483      1.399160  16.487000        0.0
    S6          57.520054   6.378240    0.252599      1.413122  16.393000        0.0
    S7          57.518013   6.345287    0.255887      1.427803  16.298000        0.0
    S8          57.516495   6.311316    0.259364      1.443274  16.200001        0.0
    S9          57.515556   6.276238    0.263051      1.459620  16.101000        0.0
    S10         57.515236   6.240000    0.266915      1.476720  16.000000        0.0

Additional options can be specified in the ``to_dataframe()`` method to access subsets of results:

.. code:: python

   zzn.to_dataframe(result_type='max', variable='Flow', include_time=True)

               Max Flow    Max Flow Time(hrs)  
   Node Label                                                                 ...                                                               
   S1          57.537834                 6.0
   CC10        57.533329                 6.0
   S3          57.529274                 6.0
   S4          57.525696                 6.0
   S5          57.522621                 6.0
   S6          57.520054                 6.0
   S7          57.518013                 6.0
   S8          57.516495                 6.0
   S9          57.515556                 6.0
   S10         57.515236                 6.0

The `ZZN` class can also be used to directly access the metadata stored within the zzn file, using the ``meta`` property - a dictionary containing the following data:


**ZZN class 'meta' keys**

.. table:: 
   :align: left

   ===============  ========================  ==============
   Key              Data Type                 Description   
   ===============  ========================  ==============
   ``zzn_name``     String                    Full path to ZZN file
   ``labels``       List of strings           Array of node labels
   ``model_title``  String                    Model title including DAT file and Flood Modeller version
   ``dt``           Float                     Model timestep (s)
   ``nnodes``       Integer                   Number of model nodes 
   ``save_int``     Float                     Simulation save interval (s)
   ===============  ========================  ==============


