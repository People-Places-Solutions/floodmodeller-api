from setuptools import setup
from pathlib import Path

with open("README.md") as f:
    readme_txt = f.read()

exec(open("floodmodeller_api/version.py").read())

setup(
    name="floodmodeller_api",
    version=__version__,
    author="Jacobs",
    author_email="joe.pierce@jacobs.com",
    packages=[
        "floodmodeller_api",
        "floodmodeller_api.units",
        "floodmodeller_api.validation",
        "floodmodeller_api.urban1d",
        "floodmodeller_api.logs",
        "floodmodeller_api.test",
        "floodmodeller_api.test.test_data"
    ],
    scripts=[str(path) for path in Path("scripts").glob("*")],
    project_urls={
        "API Documentation": "https://api.floodmodeller.com/api/",
        "Flood Modeller Homepage": "https://www.floodmodeller.com/",
        "Contact & Support": "https://www.floodmodeller.com/contact",
    },
    license="GNU General Public License V3. Copyright (C) 2023 Jacobs U.K. Limited.",
    license_file="LICENSE.txt",
    description="Extends the functionality of Flood Modeller to python users",
    long_description=readme_txt,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=["pandas>1,<3", "geopandas>0.10.1,<0.14","lxml==4.*", "tqdm==4.*", "pytest>4,<8", "pytest-mock==3.*", "plotly==5.*"],
)
