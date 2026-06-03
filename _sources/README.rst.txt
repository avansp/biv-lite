Building Documentation
======================

Building the HTML Documentation
--------------------------------

First, install the documentation dependencies::

    pip install -r docs/requirements.txt

Then build the HTML documentation::

    cd docs
    make html

The built documentation will be in ``docs/_build/html/``. Open ``docs/_build/html/index.html`` in your browser.

Building on Windows
-------------------

Use the batch file::

    cd docs
    make.bat html

Other Build Formats
-------------------

Build PDF documentation (requires LaTeX)::

    cd docs
    make pdf

Build ePub::

    cd docs
    make epub

Build plain text::

    cd docs
    make text

Cleaning Build Artifacts
------------------------

Remove all build artifacts::

    cd docs
    make clean

Using Sphinx directly
---------------------

If the Makefile doesn't work, use sphinx-build directly::

    sphinx-build -b html docs docs/_build/html

For more options::

    sphinx-build --help

Viewing the Documentation
-------------------------

After building, open the documentation in your browser. On Linux/macOS::

    open docs/_build/html/index.html

On Windows::

    start docs/_build/html/index.html

Or simply navigate to the file in your file explorer.

Live Editing
------------

For live updates while editing docs, install sphinx-autobuild::

    pip install sphinx-autobuild

Then run::

    sphinx-autobuild docs docs/_build/html

This starts a local server at ``http://localhost:8000`` that automatically rebuilds when you save files.

Troubleshooting
---------------

**Import errors during build:**

Make sure the package is importable::

    pip install --editable .

**Documentation not updating:**

Clean the build and rebuild::

    cd docs
    make clean
    make html

**Autodoc not finding classes/functions:**

Verify the module paths in conf.py are correct::

    sys.path.insert(0, os.path.abspath('..'))
    sys.path.insert(0, os.path.abspath('../src'))

For more information, see the Sphinx documentation: https://www.sphinx-doc.org/
