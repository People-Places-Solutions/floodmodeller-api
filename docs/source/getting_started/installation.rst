****************************
Installation and Importing
****************************
Before installing the Flood Modeller API, first ensure you already have Python installed on your machine (version 3.10 or greater) 
and, ideally, have a dedicated python environment set up. Flood Modeller API is regularly tested for all versions of python 3.10 
onwards. Although it may work for older versions of python, we recommend using at least v3.10 and ideally the latest stable release.
Consider using `miniforge <https://github.com/conda-forge/miniforge>`_ as a lightweight, open-source package manager. 

Once you have your Python environment set up, you can install the floodmodeller_api package directly from PyPI using the following command:

.. code:: console

   pip install floodmodeller-api

It is recommended to regularly update directly from PyPI as this will ensure you have latest version:

.. code:: console

   pip install floodmodeller-api --upgrade

To ensure the package has installed successfully, have a go at running all of the package tests:

.. code:: console

   pytest --pyargs floodmodeller_api

