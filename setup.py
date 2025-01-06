from setuptools import setup

with open("README.md") as f:
    readme_txt = f.read()

with open("floodmodeller_api/version.py") as f:
    exec(f.read())

setup(
    name="floodmodeller_api",
    version=__version__,  # type: ignore[name-defined]
    author="Jacobs",
    author_email="joe.pierce@jacobs.com",
    packages=[
        "floodmodeller_api",
        "floodmodeller_api.units",
        "floodmodeller_api.validation",
        "floodmodeller_api.urban1d",
        "floodmodeller_api.logs",
        "floodmodeller_api.toolbox",
        "floodmodeller_api.toolbox.gui",
        "floodmodeller_api.toolbox.model_build",
        "floodmodeller_api.toolbox.model_build.structure_log",
        "floodmodeller_api.toolbox.model_conversion",
        "floodmodeller_api.toolbox.model_review",
        "floodmodeller_api.toolbox.results_analysis",
        "floodmodeller_api.test",
        "floodmodeller_api.test.test_data",
        "floodmodeller_api.libs",
        "floodmodeller_api.hydrology_plus",
    ],
    entry_points={
        "console_scripts": [
            "fmapi-add_siltation = floodmodeller_api.toolbox.model_build.add_siltation_definition:main",
            "fmapi-structure_log = floodmodeller_api.toolbox.model_build.structure_log_definition:main",
        ],
    },
    project_urls={
        "API Documentation": "https://api.floodmodeller.com/api/",
        "Flood Modeller Homepage": "https://www.floodmodeller.com/",
        "Contact & Support": "https://www.floodmodeller.com/contact",
    },
    license="GNU General Public License V3. Copyright (C) 2025 Jacobs U.K. Limited.",
    license_file="LICENSE.txt",
    description="Extends the functionality of Flood Modeller to python users",
    long_description=readme_txt,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=[
        "pandas>1,<3",
        "lxml==5.*",
        "tqdm==4.*",
        "pytest>4,<8",
        "pytest-mock==3.*",
        "shapely==2.*",
        "scipy==1.*",
        "freezegun==1.*",
        "requests>2.23",
    ],
)
