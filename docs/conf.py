# docs/conf.py
project = 'biv-lite'
author = 'Avan Suinesiaputra'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx_autodoc_typehints',
]

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Auto-generate API docs
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}