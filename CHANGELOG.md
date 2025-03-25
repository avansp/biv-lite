# Change log

## v0.1.0

### Features
* Scrapped from Charlene's `biv-me` package to include only the fitted mesh model.
* The main class is `BivMesh` in the `biv_mesh.py` file.
* Refactored the package using *src_layout* layout from pypackage documentation.
* Main CLI command is `biv-lite`.
* Added volumes and mass calculation.
* Provided notebooks to plot different ways.

## v0.1.1 (24/03/2025)

### Features
* Created `BivFrames` class that handles reading multiple frames of fitted models, and all processing for full cardiac cycle.
* Added strain calculations.

### Refactoring
* `biv_plots.py` -> `plots.py`
* `biv_measures.py` -> `measures.py`