*************************
Individual Unit Classes
*************************
This section summarises all the Flood Modeller unit types which are supported in the API. Being 'supported' means that the units can be read, 
updated and written via the API directly. Unit types which are 'unsupported' are still able to be within IED and DAT files accessed through 
the API but cannot be read or updated.


.. _boundary_units:

Boundary units
--------------
``QTBDY()``
~~~~~~~~~~~

.. autoclass:: floodmodeller_api.units.QTBDY


``HTBDY()``
~~~~~~~~~~~

.. autoclass:: floodmodeller_api.units.HTBDY


``QHBDY()``
~~~~~~~~~~~

.. autoclass:: floodmodeller_api.units.QHBDY


``REFHBDY()``
~~~~~~~~~~~~~~

.. autoclass:: floodmodeller_api.units.REFHBDY

.. _section_units:

Section units
-------------
``RIVER()``
~~~~~~~~~~~

.. autoclass:: floodmodeller_api.units.RIVER
  
   .. autoproperty:: conveyance

``INTERPOLATE()``
~~~~~~~~~~~~~~~~~

.. autoclass:: floodmodeller_api.units.INTERPOLATE

``REPLICATE()``
~~~~~~~~~~~~~~~

.. autoclass:: floodmodeller_api.units.REPLICATE

.. _conduit_units:

Conduit units
-------------
``CONDUIT()``
~~~~~~~~~~~~~~

.. autoclass:: floodmodeller_api.units.CONDUIT

.. _structure_units:

Structure units
---------------
``BRIDGE()``
~~~~~~~~~~~~~

.. autoclass:: floodmodeller_api.units.BRIDGE

``RNWEIR()``
~~~~~~~~~~~~~

.. autoclass:: floodmodeller_api.units.RNWEIR

``SLUICE()``
~~~~~~~~~~~~~

.. autoclass:: floodmodeller_api.units.SLUICE

``ORIFICE()``
~~~~~~~~~~~~~

.. autoclass:: floodmodeller_api.units.ORIFICE

``SPILL()``
~~~~~~~~~~~~~

.. autoclass:: floodmodeller_api.units.SPILL


``CRUMP()``
~~~~~~~~~~~~~

.. autoclass:: floodmodeller_api.units.CRUMP

``FLAT_V_WEIR()``
~~~~~~~~~~~~~~~~~

.. autoclass:: floodmodeller_api.units.FLAT_V_WEIR

``OUTFALL()``
~~~~~~~~~~~~~

.. autoclass:: floodmodeller_api.units.OUTFALL

.. _loss_units:

Loss units
-------------
``BLOCKAGE()``
~~~~~~~~~~~~~~

.. autoclass:: floodmodeller_api.units.BLOCKAGE

``CULVERT()``
~~~~~~~~~~~~~

.. autoclass:: floodmodeller_api.units.CULVERT