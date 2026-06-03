Installation
=============

Quick Install
-------------

Install biv-lite from GitHub::

    pip install git+https://github.com/avansp/biv-lite

Verify the installation::

    biv-lite --help

Development Installation
------------------------

To install for development::

    git clone https://github.com/avansp/biv-lite
    cd biv-lite
    pip install -r requirements.txt
    pip install --editable .

For Jupyter notebook support with interactive visualization::

    pip install trame_jupyter_extension

Run tests to verify everything works::

    pytest

Requirements
------------

- Python >= 3.9
- NumPy
- SciPy
- Pandas
- PyVista (for visualization)
- Typer (for CLI)
- Click (dependency)

See ``requirements.txt`` for complete dependency list.
