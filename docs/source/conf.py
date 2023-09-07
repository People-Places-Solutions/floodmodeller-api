# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath("..\\.."))
print(sys.path)


# -- Project information -----------------------------------------------------

project = "Flood Modeller Python API"
copyright = "2023, Jacobs"
author = "Joe Pierce"

# The full version, including alpha/beta/rc tags
release = "0.4.1"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon", "sphinx_panels"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"
html_logo = "_static/flood-modeller-logo-hero-image.png"
html_theme_options = {
    "navbar_end": [
        "search-field.html"
    ],  # ["navbar-icon-links.html", "search-field.html"],
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
