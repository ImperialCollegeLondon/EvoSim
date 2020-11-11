# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------


# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
import sys

# documentation root, use os.path.abspath to make it absolute, like shown here.
from datetime import datetime  # noqa: E402

if sys.version_info >= (3, 8) and sys.platform == "win32":
    # See: https://github.com/jupyter/jupyter_client/issues/583
    import asyncio

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# -- Project information -----------------------------------------------------

project = "EvoSim"
copyright = f"{datetime.today().year}, Imperial College London"
author = "Research Computing Service, Imperial College London"

# The full version, including alpha/beta/rc tags
release = "0.2.0"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "recommonmark",
    "nbsphinx",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["source/generated/index.rst"]

modindex_common_prefix = ["evosim"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("http://docs.scipy.org/doc/numpy/", None),
    "pandas": ("http://pandas.pydata.org/pandas-docs/stable", None),
    "sklearn": ("https://scikit-learn.org/stable", None),
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "alabaster"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []

autodoc_typehints = "description"

html_show_sourcelink = True

doctest_global_setup = """
import pandas as pd
import numpy as np
import evosim

pd.options.mode.chained_assignment = "raise"
pd.options.display.precision = 2
pd.options.display.max_categories = 8
pd.options.display.max_rows = 20
pd.options.display.max_columns = 10
pd.options.display.width = 88
np.set_printoptions(linewidth=88)
"""


def generate_docstring_files():
    """Generate automodule files so they are split into different HTML pages."""
    import evosim
    from pathlib import Path
    from types import ModuleType
    from textwrap import dedent

    location = Path(__file__).parent / "source" / "generated"
    location.mkdir(exist_ok=True)
    index = dedent(
        """
        .. toctree::
           :maxdepth: 2
           :caption: Sub-packages:

        """
    )
    for attr in evosim.__all__:
        if not isinstance(getattr(evosim, attr), ModuleType):
            continue
        (location / f"{attr}.rst").write_text(f".. automodule :: evosim.{attr}")
        index += f"   generated/{attr}\n"
    (location / "index.rst").write_text(index)


def generate_installation():
    """Generate installation instructions from readme."""
    from pathlib import Path

    readme = (Path(__file__).parent.parent / "README.md").read_text()
    location = Path(__file__).parent / "source" / "generated"
    location.mkdir(exist_ok=True)
    (location / "installation.md").write_text(
        "# Installation\n" + readme[readme.find("# Installation") :].replace("#", "##")
    )


def copy_notebooks():
    from shutil import copytree
    from pathlib import Path

    src = Path(__file__).parent.parent / "notebooks"
    dst = Path(__file__).parent / "source" / "generated" / "howto"
    copytree(src, dst, dirs_exist_ok=True)


def generate_yaml_inputs():
    from shutil import copytree
    from pathlib import Path
    import evosim

    dst = Path(__file__).parent / "source" / "generated" / "examples"
    copytree(evosim.io.EXEMPLARS["examples"], dst, dirs_exist_ok=True)

    prefix = Path(__file__).parent / "source" / "generated" / "yaml"
    prefix.mkdir(parents=True, exist_ok=True)

    registries = [
        evosim.fleet.register_fleet_generator,
        evosim.charging_posts.register_charging_posts_generator,
        evosim.matchers.register_matcher,
        evosim.objectives.register_objective,
        evosim.allocators.register_allocator,
    ]
    for registry in registries:
        name = registry.name.replace(" ", "-")
        (prefix / f"{name}.rst").write_text(registry.parameter_docs)


generate_docstring_files()
generate_installation()
generate_yaml_inputs()
copy_notebooks()
