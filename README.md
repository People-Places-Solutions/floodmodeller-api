![FM Logo](https://raw.githubusercontent.com/People-Places-Solutions/floodmodeller-api/main/docs/source/_static/flood-modeller-logo-hero-image.png)


[![PyPI Latest Release](https://img.shields.io/pypi/v/floodmodeller-api.svg)](https://pypi.org/project/floodmodeller-api/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://github.com/People-Places-Solutions/floodmodeller-api/blob/main/LICENSE.txt)
![example workflow](https://github.com/People-Places-Solutions/floodmodeller-api/actions/workflows/run_tests.yml/badge.svg)
[![Downloads](https://static.pepy.tech/personalized-badge/floodmodeller-api?period=month&units=international_system&left_color=black&right_color=orange&left_text=PyPI%20downloads%20per%20month)](https://pepy.tech/project/floodmodeller-api)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


# Flood Modeller Python API
This python package is designed to be used in conjunction with your installation of Flood Modeller to provide users with a set of tools to extend the capabilities of Flood Modeller and build into automated workflows.

![API Overview](https://raw.githubusercontent.com/People-Places-Solutions/floodmodeller-api/main/docs/source/getting_started/api_overview_small.png)

## Installation
You can install the floodmodeller_api package from PyPI with the following command:

```
pip install floodmodeller-api
```

Python 3.6 or greater is required, but we would recommend using a more recent version (3.9+).

Once you have installed floodmodeller_api to your python environment, you can import the package with:

```python
import floodmodeller_api  # imports the full package
from floodmodeller_api import DAT, ZZN, IEF, IED  # imports individual classes (recommended)
```
## How to use

The best place to start is to go directly to the [Flood Modeller Python API Documentation](https://api.floodmodeller.com/api/)

The Flood Modeller Python API is designed for users already familiar with both Flood Modeller and Python. The API is built up using distinct python classes for each of the key Flood Modeller file formats as well as key themes. The purpose of the API is not to provide ready-to-use tools for specific tasks, as there is an extensive set of tools already provided within Flood Modeller, many of which can be called from both within and outside of the Flood Modeller software. **Instead, this API provides the building blocks for users to build their own custom workflows and tools which can integrate seamlessly with Flood Modeller.**

## [Show and Tell](https://github.com/People-Places-Solutions/floodmodeller-api/discussions) 
In the spirit of open source, we encourage you to share any interesting scripts or tools you have developed using the Flood Modeller Python API. 
To do this, please get involved [in the discussions section here](https://github.com/People-Places-Solutions/floodmodeller-api/discussions). This
is also a great place to explore different ways that people have used the API.

--------------------

### A simple example of running a model and fetching the results...

![gif demo](https://raw.githubusercontent.com/People-Places-Solutions/floodmodeller-api/main/docs/source/_static/ief_zzn_demo.gif)




