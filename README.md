<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/People-Places-Solutions/floodmodeller-api/main/docs/source/_static/flood-modeller-logo-hero-image-dark.png">
  <img alt="FM Logo" src="https://raw.githubusercontent.com/People-Places-Solutions/floodmodeller-api/main/docs/source/_static/flood-modeller-logo-hero-image.png">
</picture>


[![PyPI Latest Release](https://img.shields.io/pypi/v/floodmodeller-api.svg)](https://pypi.org/project/floodmodeller-api/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://github.com/People-Places-Solutions/floodmodeller-api/blob/main/LICENSE.txt)
![Unit Tests](https://github.com/People-Places-Solutions/floodmodeller-api/actions/workflows/run_tests.yml/badge.svg)
![Lint](https://github.com/People-Places-Solutions/floodmodeller-api/actions/workflows/run_linters.yml/badge.svg)
[![Downloads](https://static.pepy.tech/personalized-badge/floodmodeller-api?period=month&units=international_system&left_color=black&right_color=orange&left_text=PyPI%20downloads%20per%20month)](https://pepy.tech/project/floodmodeller-api)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)



# Flood Modeller Python API

#### 🌏  Open in Cloud IDEs

Click any of the buttons below to start a new development environment to demo or contribute to the codebase without having to install anything on your machine:

[![Open in Glitch](https://img.shields.io/badge/Open%20in-Glitch-blue?logo=glitch)](https://glitch.com/edit/#!/import/github/people-places-solutions/floodmodeller-api)
[![Edit in Codesandbox](https://codesandbox.io/static/img/play-codesandbox.svg)](https://codesandbox.io/s/github/people-places-solutions/floodmodeller-api)
[![Open in Repl.it](https://replit.com/badge/github/withastro/astro)](https://replit.com/github/people-places-solutions/floodmodeller-api)
[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/people-places-solutions/floodmodeller-api)
[![Try in GitHub Codespaces!](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&repo=473959586&quickstart=1)
[![Open in Codeanywhere](https://codeanywhere.com/img/open-in-codeanywhere-btn.svg)](https://app.codeanywhere.com/#https://github.com/People-Places-Solutions/floodmodeller-api)

This python package is designed to be used in conjunction with your installation of Flood Modeller to provide users with a set of tools to extend the capabilities of Flood Modeller and build into automated workflows.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/People-Places-Solutions/floodmodeller-api/main/docs/source/getting_started/api_overview_dark.png">
  <img alt="API Overview" src="https://raw.githubusercontent.com/People-Places-Solutions/floodmodeller-api/main/docs/source/getting_started/api_overview.png">
</picture>

## Installation
You can install the floodmodeller_api package from PyPI with the following command:

```
pip install floodmodeller-api
```

Python 3.10 or greater is required.

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

### Youtube mini tutorials
These videos give you a quick overview of some of the basics of using the Flood Modeller API

**Running a simulation**

<a href="https://www.youtube.com/watch?v=WfCNkC44shI?vq=1080p" target="_blank"><img src="https://github-production-user-asset-6210df.s3.amazonaws.com/56606086/253010465-8a714e5b-9364-4073-9af5-679dab0a8249.png" width="400"></a>

**Using the codespace**

<a href="https://www.youtube.com/watch?v=BWV3A7R0fbM?vq=1080p" target="_blank"><img src="https://github-production-user-asset-6210df.s3.amazonaws.com/56606086/257823093-545e0b61-4252-4ed3-8870-405fa869461d.png" width="400"></a>

**Extract ReFH2 csv data into IEDs and QTBDYs**

<a href="https://www.youtube.com/watch?v=E9JMQ2DKr0c?vq=1080p" target="_blank"><img src="https://github-production-user-asset-6210df.s3.amazonaws.com/56606086/257824500-39c991cd-8bad-4e08-bd39-0f26981d173b.png" width="400"></a>



