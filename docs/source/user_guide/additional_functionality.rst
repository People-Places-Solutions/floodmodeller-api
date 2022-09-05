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