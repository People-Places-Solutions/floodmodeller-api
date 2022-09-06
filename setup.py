from setuptools import setup

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
    ],
    scripts=[],
    project_urls={
        "API Documentation": "https://help.floodmodeller.com/api/",
        "Flood Modeller Homepage": "https://www.floodmodeller.com/",
        "Contact & Support": "https://www.floodmodeller.com/contact",
    },
    license="GNU General Public License V3. Copyright (C) 2022 Jacobs U.K. Limited.",
    license_file="LICENSE.txt",
    description="Extends the functionality of Flood Modeller to python users",
    long_description=readme_txt,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=["pandas", "lxml", "tqdm"],
)
