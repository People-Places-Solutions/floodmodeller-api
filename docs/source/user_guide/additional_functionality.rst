.. ifconfig:: internal

   .. ipython:: python
      
      import os
      os.chdir("floodmodeller_api/test/test_data")

Additional Functionality
=========================

This section provides information on some additional functionality of the API that is not
specific to any single class.

Difference and equivalence methods
-----------------------------------
When working with the API, it is often useful to understand whether two instances of a class
are equal, or if not, what the differences are. In general, the API considers two instances
equal if they contain the exact same data and therefore would write the same output. Some
attributes such as the filepath do not need to be the same for them to be considered equal.

Two instances of the same class can now be tested using ``==`` to check whether they are 
equal.

.. ipython:: python 

    from floodmodeller_api import DAT

    dat_a = DAT("EX18.DAT")
    dat_b = DAT("EX18.DAT")

    dat_a == dat_b

    # Make some changes to one
    dat_a.sections["S3"].dist_to_next += 20
    dat_a.general_parameters["Min Depth"] = 0.2

    dat_a == dat_b


In addition, a detailed breakdown of any differences can be found using the ``.diff()`` 
method:

.. ipython:: python
    
    dat_a.diff(dat_b)  # prints a list of differences to terminal
 
Currently, the ``==`` and ``.diff()`` methods is supported for the following classes:

- DAT
- IED
- IEF
- INP
- XML2D
- All 1D River Unit classes 

File Backups
------------
The API automatically backs up any data files you load via the DAT, IED, IEF, INP and XML2D classes. The files are backed up in your OS temporary directory (see `tempfile.gettempdir()`). 
You can restore backups via the the `.file.restore()` method. Currently this restores the latest backup, but if you want to restore a specific backup then you list the backups and navigate to the file via the os file directory.

.. code:: python

    # Load the DAT
    # Automatically backs up the file if it has changes since the last backup
    dat = DAT("a_dat_file.DAT")
    # List the available backups
    backups = dat.file.list_backups()
    # Restore the latest backup to a file
    backups[0].restore(to = "restore-file.DAT")
    # Restore an older backup
    backups[6].restore(to = "restore-file.DAT")


JSON methods
-------------
Any flood modeller object can be converted to a JavaScript Object Notation (JSON) string, and vice 
versa. To convert to JSON, simply call the ``.to_json()`` method on any API class to return a valid
json string. Conversely, any valid json string produced by the API can be converted back into its
equivalent API instance using the ``.from_json()`` constructor on any API class.

To convert a flood modeller object to a JSON string:

.. ipython:: python
    
    from floodmodeller_api import IEF
    ief = IEF("network.ief")

    json_string = ief.to_json()
    print(json_string)

To convert a JSON file to a flood modeller object:

.. ipython:: python

    ief = IEF.from_json(json_string)
    ief

To convert a single River Section unit to JSON:

.. ipython:: python
    
    from floodmodeller_api import DAT
    dat = DAT("EX18.DAT")
    river_unit_json = dat.sections["S3"].to_json()
    print(river_unit_json)