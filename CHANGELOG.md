# Change log

## v0.1.0

### Features
* Scrapped from Charlene's `biv-me` package to include only the fitted mesh model.
* The main class is `BivMesh` in the `biv_mesh.py` file.
* Refactored the package using *src_layout* layout from pypackage documentation.
* Main CLI command is `biv-lite`.
* Added volumes and mass calculation.
* Provided notebooks to plot different ways.

## v0.2.0 (24/03/2025)

### Features
* Created `BivFrames` class which is a list of `BivMesh` with some extra props & methods.
* Added UI app
* Added interpolation function for BivFrames
* Created `BivParametric` class which can generate interpolated biventricular models in continuous temporal domain t=[0,1].

### Refactoring
* `biv_plots.py` -> `plots.py`
* `biv_measures.py` -> `measures.py`
* Plot a complete biv mesh is now written in `vis.py` file
* `to_pyvista_faces` function is inside `utils.py` file
* All typer app's are in `app` subfolder, except for `main.py`
* `BivMotionUI` class is separated in `biv_motion_ui.py` file

## v0.2.1 (11/04/2025)

### Patching
* Added `metadata` attribute in the `BivMesh`, `BivFrames`, and `BivParametric` to contains any information you want as a dictionary.
* Added the possibility if a control point is empty (empty `BivMesh`).

## v0.2.2 (10/06/2025)

### Patching
* Updated python to 3.12
* Updated pyvista package to allow trame backend for jupyter notebook.