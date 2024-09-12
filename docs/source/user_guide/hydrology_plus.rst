.. _hplus:

Hydrology+ 
=============
Summary
--------
Hydrology+ is a powerful new feature as of version 7 of Flood Modeller which integrates the 
industry-standard WINFAP and ReFH2 hydrological packages with Flood Modeller, introducing enhanced 
flexibility and time-savings for both hydrologists and hydraulic modellers.

For more information on Hydrology+ go to: `floodmodeller.com/hydrologyplus <https://www.floodmodeller.com/hydrologyplus>`_

Whilst the majority of hydrological analysis can be done within the Flood Modeller interface, the 
Flood Modeller API offers integration with Hydrology+ through the ``floodmodeller_api.hydrology_plus``
module in 3 ways:
- Support for exported flow data from Hydrology+ using the ``HydrologyPlusExport`` class
- Support for quickly generating sets of IEF and 2D XML files based on exported flow data
- Direct connection to the Hydrology+ database for advanced analysis (*power users only*)

Hydrology+ exported flow data
------------------------------

Once hydrological analysis has been undertaken in Flood Modeller, the resultant flow data can be
exported into csv format, containing metadata as well as flow data for a combination of different
return periods, storm durations and scenarios.

These exported csv files can be read using the API class ``HydrologyPlusExport`` or using the helper
functions ``load_hydrology_plus_csv_export()`` or ``read_file``:

.. ipython:: python
   
    from floodmodeller_api.hydrology_plus import load_hydrology_plus_csv_export, HydrologyPlusExport;
    from floodmodeller_api import read_file;
    HydrologyPlusExport("example_h+_export.csv"); # Load using class directly
    load_hydrology_plus_csv_export("example_h+_export.csv"); # Load using H+ helper function
    read_file("example_h+_export.csv"); # Load using main API helper function

Once loaded, the ``HydrologyPlusExport`` class can access the metadata and flow data.

.. ipython:: python

    hplus = HydrologyPlusExport("example_h+_export.csv")
    hplus.metadata
    hplus.return_periods
    hplus.storm_durations
    hplus.scenarios
    hplus.data.head()

    @savefig hplus_plot.png
    hplus.data.plot(ylabel="Flow(m3/s)", legend=False);

You can also access specific event flow data by either passing in the full event string or the 
individual components in the ``.get_event()`` method:

.. ipython:: python

    event_flow = hplus.get_event(
        scenario="2020 Upper",
        storm_duration=11.0,
        return_period=1,
    )
    event_flow

    @savefig event_plot.png
    event_flow.plot(ylabel="Flow(m3/s)");


Generating IEF and 2D XML data
--------------------------------

tbc

Connecting to Hydrology+ SQL database
--------------------------------------


Reference
--------------
.. autoclass:: floodmodeller_api.hydrology_plus.HydrologyPlusExport

   .. autoproperty:: data

   .. autoproperty:: metadata

   .. autoproperty:: return_periods

   .. autoproperty:: storm_durations
   
   .. autoproperty:: scenarios

   .. automethod:: get_event