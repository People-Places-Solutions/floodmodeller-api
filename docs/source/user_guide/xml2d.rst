XML2D Class
=====================================================
Summary
--------
The ``XML2D`` class is used to read and update Flood Modeller's 2D XML file format. 
The class is initiated with the full filepath of an xml file to load an existing 2D model. 

.. attention::
   
   The API functionality for 2D XML files is currently in development and should be 
   treated as experimental.

.. admonition:: *New in version 0.4.1*

   2D elements can now be added and removed from an XML2D instance by simply adding/removing
   them from the relevant section

.. code:: python

    from floodmodeller_api import XML2D

    model = XML2D('path/to/2d_model.xml') # Loads existing XML file into memory

Once you have initialised an XML class, all the information defining the model will be stored
in the following attributes (some of these attributes may not be present in the xml file and 
will therefore return ``None`` )

-  ``.name`` - 2D Model name
-  ``.link1d`` - A list of 1 or more 1D links, each containing a dictionary of parameters
   including the link shapefile and ief file. 
-  ``.logfile`` - Location of model log
-  ``.domains`` - A dictionary of model domains, with each domain_id as the keys. Each model
   domain is then a nested dictionary of categories and values.
-  ``.restart_options``
-  ``.advanced_options``
-  ``.processor``
-  ``.unit_system``
-  ``.description``

There are many different parameters which can be set in a 2D model. All of these are able to
be read via the XML2D class if they appear in the xml file. Within each main attribute, the
naming and structure of options is consistent with the structure in the xml file itself. 
In cases where an option has just a single value, the value and option name will appear as
a key-pair in the dictionary. In cases where an option has attributes as well as a value, 
the attributes will also appear, and the value will be accessible through the 'value' key.

Any option where multiple values can be provided (e.g. topography files) will be present 
as a list of dictionaries, whereas options where only one value can be required will be 
a single dictionary.

A typical example of the available options for a single 2D domain is shown below:

.. code:: python
    
    model = XML2D('path/to/2d_model.xml')

    # Access a specific model domain by name
    model.domains["Domain1 20m Q"]
    >>>
        {
            "domain_id": "Domain1 20m Q",
            "computational_area": {
                "xll": 538000.0,
                "yll": 177000.0,
                "dx": 20,
                "nrows": 200,
                "ncols": 300,
                "active_area": "GIS\\Active_Area1.shp",
                "rotation": 0
            },
            "topography": ["GIS\\5M_DTM_1.asc"],
            "time": {
                "start_time": "00:00:00",
                "start_date": "1/1/2000",
                "total": {
                    "unit": "second",
                    "value": 43200
                }
            },
            "run_data": {
                "time_step": 2,
                "scheme": "ADI"
            },
            "initial_conditions": {
                "type": "globalwaterlevel",
                "value": 0.0
            },
            "roughness": [
                {
                    "law": "manning",
                    "type": "global",
                    "value": 0.05
                }
            ],
            "output_results": {
                "output": [
                    {
                        "output_id": "",
                        "format": "SMS9",
                        "variables": "DepthVelocityElevationFlow",
                        "frequency": 300
                    }
                ],
                "massfile": {
                    "frequency": "10",
                    "value": "Domain1+2_QH_2DMB_1.csv"
                }

Accessing individual elements can be achieved by using the relevant keys:

.. code:: python

    model.domains["Domain1 20m Q"]["computational_area"]["dx"]
    >>> 20

Any element can be updated by simply updating editing the value in the dictionary. For example
to change the 1d link shapefile:

.. code:: python

    model.link1d[0]["link"]
    >>> 'GIS\\Link1+2_QH.shp'

    model.link1d[0]["link"] = "GIS\\Link3_New.shp"

Information on all the possible options for 2D XML files can be derived from the xml schema file
`here <http://schema.floodmodeller.com/5.1/2d.xsd>`_. Any edits to 2D XML files are first 
validated against this schema before saving, an exception will be raised if the data is not
valid.

An XML2D instance can be updated in place and saved in the same way as for all other files
supported by the API using the ``.update()`` and ``.save()`` methods respectively.

Add and remove functionality
--------------------------------
We can update the xml file directly from the API by adding and removing properties. 
Imagine that we start with an almost blank xml file that passes the validation, 

.. code:: python

    model = XML2D()

First we can change a variable that already exists. For instance we can change the value of 
the topography,

.. code:: python

    model.domains[domain_name]["topography"] = 'path/to/my_topography.asc'

We can edit any value that is already in the xml tree in the same way by overwritting it, another 
example is we can change the end time of the computation,

.. code:: python

    model.domains[domain_name]["time"]["total"] = 1.00

We can also add information to a key that does not exist yet, such as roughness. We first begin 
by defining an empty list and then populate it with a dictionary, we can keep appending so we have 
as many dictionaries in a list as we want,

.. code:: python
    
    model.domains[domain_name]["roughness"] = [] # created an empty list we can append dictionaries to
    model.domains[domain_name]["roughness"].append(
        {'type': 'file', 'law': 'manning', 'value': 'path/to/my_roughness_file.shp'}
    )
    # adding second roughness file.
    model.domains[domain_name]["roughness"].append(
        {'type': 'file', 'law': 'manning', 'value': 'path/to/my_second_roughness_file.shp'}
    )

If we wanted to edit one of the roughness values then we would need to use the list indexing, to 
change the file for the first roughness,

.. code:: python

    model.domains[domain_name]["roughness"][0]["value"] = 'path/to/my_new_roughness_file.shp'

To remove values or keys from the xml file we can use ``del ...`` followed by the part you want to 
remove. If we want to remove the second roughness entry for instance then,

.. code:: python

    del model.domains[domain_name]["roughness"][1]

Further, we can remove all information relating to the key roughness,

.. code:: python

    del model.domains[domain_name]["roughness"]

The xml2d files should follow the Flood Modeller xsd schema - preferably the most recent version 
but backwards compatability is possible.

Reference
--------------
.. autoclass:: floodmodeller_api.XML2D
    
   .. automethod:: update

   .. automethod:: save

   .. automethod:: diff

   .. automethod:: simulate

Examples
-----------
**Example 1 - Updating DTM file** 

This is a simple example showing how you would update the dtm referenced in the 2D model

.. code:: python

    # Import modules
    from floodmodeller_api import XML2D

    # Initialise DAT class
    model = XML2D("path/to/2d_model.xml")

    # Define new dtm data path
    new_dtm = "GIS/new_dtm.asc"

    # Iterate through all 2D domains
    for _, domain in model.domains.items():
        domain["topography"][0] = new_dtm  # update the dtm file

    model.save("path/to/2d_model_v2.xml") # Save to new location


