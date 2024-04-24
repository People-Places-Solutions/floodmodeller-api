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

.. code:: python 

    dat_a = DAT('some_network.dat')
    dat_b = DAT('another_similar_network.dat')

    if dat_a == dat_b:  # returns True/False
        print('Files are equivalent')
    else:
        print('Files not equivalent')


In addition, a detailed breakdown of any differences can be found using the ``.diff()`` 
method:

.. code:: python
    
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

.. code:: python

    dat = DAT('some_network.dat')

    obj_json = dat.to_json()

To convert a JSON file to a flood modeller object:

.. code:: python

    dat = DAT.from_json(json_string)

To convert a single River Section unit to JSON:

.. code:: python
    
    dat = DAT("some_network.dat")
    river_unit_json = dat.sections["some_unit"].to_json()