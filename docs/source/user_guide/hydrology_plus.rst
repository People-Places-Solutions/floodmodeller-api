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

- Support for exported flow data from Hydrology+ using the :class:`~floodmodeller_api.hydrology_plus.HydrologyPlusExport` class
- Support for quickly generating sets of IEF files based on exported flow data
- **[Not yet available]** Direct connection to the Hydrology+ database for advanced analysis (*power users only*)

Hydrology+ exported flow data
------------------------------

Once hydrological analysis has been undertaken in Flood Modeller, the resultant flow data can be
exported into csv format, containing metadata as well as flow data for a combination of different
return periods, storm durations and scenarios.

These exported csv files can be read using the API class :class:`~floodmodeller_api.hydrology_plus.HydrologyPlusExport` 
or using the helper functions ``load_hydrology_plus_csv_export()`` or :func:`~floodmodeller_api.read_file`:

.. ipython:: python
   
    from floodmodeller_api.hydrology_plus import load_hydrology_plus_csv_export, HydrologyPlusExport;
    from floodmodeller_api import read_file;
    HydrologyPlusExport("example_h+_export.csv"); # Load using class directly
    load_hydrology_plus_csv_export("example_h+_export.csv"); # Load using H+ helper function
    read_file("example_h+_export.csv"); # Load using main API helper function

Once loaded, the :class:`~floodmodeller_api.hydrology_plus.HydrologyPlusExport` class can access the metadata and flow data.

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
individual components in the :meth:`~floodmodeller_api.hydrology_plus.HydrologyPlusExport.get_event_flow` method:

.. ipython:: python

    event_flow = hplus.get_event_flow(
        scenario="2020 Upper",
        storm_duration=11.0,
        return_period=100,
    )
    event_flow

    @savefig event_plot.png
    event_flow.plot(ylabel="Flow(m3/s)");

A similar option is available to return a single event flow as a QTBDY unit. For example, to extract 
a QTBDY and add into a new IED file we use the :meth:`~floodmodeller_api.hydrology_plus.HydrologyPlusExport.get_qtbdy` method:

.. ipython:: python

    from floodmodeller_api import IED;
    from floodmodeller_api.units import QTBDY;

    qtbdy = hplus.get_qtbdy(
        qtbdy_name="New_QT001",
        scenario="2020 Upper",
        storm_duration=11.0,
        return_period=100,
    )
    new_ied = IED();
    new_ied.boundaries[qtbdy.name] = qtbdy;
    print(new_ied._write())


Generating IEF data
--------------------------------

With the :class:`~floodmodeller_api.hydrology_plus.HydrologyPlusExport` class instantiated, we can generate
IEF files with flowtimeprofiles based on the data in the CSV. This can be done based on a blank IEF 
with no other attributes set, or based on a given template IEF. We can generate a full set of IEF files
using the :meth:`~floodmodeller_api.hydrology_plus.HydrologyPlusExport.generate_iefs` method, or a 
single ief using :meth:`~floodmodeller_api.hydrology_plus.HydrologyPlusExport.generate_ief`:

.. ipython:: python

    ief = hplus.generate_ief(node_label="INFLOW_001", event="2020 Upper - 11 - 100");
    
    ief
    print(ief._write())

    iefs = hplus.generate_iefs(node_label="INFLOW_001");
    for ief in iefs:
        print(ief)



Reference
--------------
.. autoclass:: floodmodeller_api.hydrology_plus.HydrologyPlusExport

   .. autoproperty:: data

   .. autoproperty:: metadata

   .. autoproperty:: return_periods

   .. autoproperty:: storm_durations
   
   .. autoproperty:: scenarios

   .. automethod:: generate_ief

   .. automethod:: generate_iefs

   .. automethod:: get_event_flow

   .. automethod:: get_flowtimeprofile

   .. automethod:: get_qtbdy