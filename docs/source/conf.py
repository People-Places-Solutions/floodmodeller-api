# Configuration file for the Sphinx documentation builder.  # noqa: INP001
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path("..\\..").resolve()))


# -- Project information -----------------------------------------------------

project = "Flood Modeller Python API"
project_copyright = "2025, Jacobs"
author = "Joe Pierce"

# The full version, including alpha/beta/rc tags
release = "0.5.0"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.ifconfig",
    "sphinx_design",
    "IPython.sphinxext.ipython_directive",
    "IPython.sphinxext.ipython_console_highlighting",
    "matplotlib.sphinxext.plot_directive",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns: list[str] = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"
html_logo = "_static/flood-modeller-logo-hero-image.png"
html_theme_options = {
    "navbar_end": ["search-field.html"],  # ["navbar-icon-links.html", "search-field.html"],
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/People-Places-Solutions/floodmodeller-api",
            "icon": "fab fa-github",
        },
        {
            "name": "Contact Us",
            "url": "https://www.floodmodeller.com/contact",
            "icon": "fas fa-inbox",
        },
        {
            "name": "About Flood Modeller",
            "url": "https://www.floodmodeller.com/about",
            "icon": "fas fa-question",
        },
        {
            "name": "YouTube",
            "url": "https://www.youtube.com/user/floodmodeller",
            "icon": "fab fa-youtube",
        },
        {
            "name": "LinkedIn",
            "url": "https://www.linkedin.com/showcase/floodmodeller/",
            "icon": "fab fa-linkedin",
        },
    ],
    "footer_items": ["footer_links", "icon-links", "copyright", "sphinx-version"],
}

html_favicon = "_static/fm_fav.png"

html_sidebars = {"**": ["sidebar-nav-bs.html"]}


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_css_files = ["fmapi.css"]
html_extra_path = ["on_a_page"]


def setup(app):
    app.add_config_value("internal", "", "env")
