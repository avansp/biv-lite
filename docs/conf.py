# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Add the parent directory to the path for autodoc to find modules
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../src'))

# -- Project information -----------------------------------------------
project = 'biv-lite'
author = 'Avan Suinesiaputra'
release = '0.2.4'

# -- General configuration --------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',           # Automatically extract docstrings
    'sphinx.ext.autosummary',       # Generate summary tables
    'sphinx.ext.napoleon',          # Parse Google/NumPy docstrings
    'sphinx.ext.intersphinx',       # Link to external documentation
    'sphinx.ext.viewcode',          # Add links to source code
    'sphinx.ext.coverage',          # Check documentation coverage
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Autodoc Configuration --------------------------------------------------
autodoc_default_options = {
    'members': True,                    # Document all members
    'member-order': 'bysource',         # Order by source appearance
    'special-members': '__init__',      # Include special methods like __init__
    'undoc-members': False,             # Don't include undocumented members
    'show-inheritance': True,           # Show class inheritance
}

autosummary_generate = True             # Generate summary files automatically

# -- Napoleon Configuration -------------------------------------------------
# Configure Napoleon for Google-style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False

# -- Options for HTML output ------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Intersphinx Configuration -----------------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
}
