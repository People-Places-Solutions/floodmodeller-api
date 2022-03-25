# Flood Modeller Python API
This python package is designed to be used in conjunction with your install of Flood Modeller to provide users with a set of tools to extend the capabilities of Flood Modeller and build into automated workflows.

![API Overview](https://raw.githubusercontent.com/People-Places-Solutions/floodmodeller-api/main/docs/source/getting_started/api_overview_small.png?token=GHSAT0AAAAAABS4AL6AH5EWEXPDWKM7LCNIYSG42CA)

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

The best place to start is to go directly to the [Flood Modeller Python API Documentation](https://help.floodmodeller.com/api/)

The Flood Modeller Python API is designed for users already familiar with both Flood Modeller and Python. The API is built up using distinct python classes for each of the key Flood Modeller file formats as well as key themes. The purpose of the API is not to provide ready-to-use tools for specific tasks, as there is an extensive set of tools already provided within Flood Modeller, many of which can be called from both within and outside of the Flood Modeller software. **Instead, this API provides the building blocks for users to build their own custom workflows and tools which can integrate seamlessly with Flood Modeller.**


![gif demo](https://raw.githubusercontent.com/People-Places-Solutions/floodmodeller-api/main/docs/source/_static/ief_zzn_demo.gif?token=GHSAT0AAAAAABS4AL6A3Q4YEVE3XWIGXG6CYSG44SQ)
