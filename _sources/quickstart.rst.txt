Quick Start
===========

Loading a Fitted Model
----------------------

The main class is :class:`BivMesh`. Load a fitted model and inspect it::

    from biv_lite import BivMesh

    # Load a fitted model (388 control points)
    biv = BivMesh.from_fitted_model("tests/fitted_model.txt")
    print(biv)

Output::

    <BivMesh> object
      Label: biv_mesh
      Control points: (388, 3), dtype: float64
      Vertices: (5810, 3), dtype: float64
      Faces: (11920, 3), dtype: int64
      Components: AORTA_VALVE, AORTA_VALVE_CUT, LV_ENDOCARDIAL, ...

Extracting Mesh Components
---------------------------

Access specific cardiac structures::

    from biv_lite import BivMesh
    from biv_lite.biv_mesh import Components

    biv = BivMesh.from_fitted_model("tests/fitted_model.txt")

    # Get left ventricle endocardial surface
    lv_endo = biv.lv_endo()

    # Get right ventricle epicardial surface
    rv_epi = biv.rv_epi()

Computing Volumes and Mass
---------------------------

Calculate cardiac measurements::

    from biv_lite import BivMesh

    biv = BivMesh.from_fitted_model("tests/fitted_model.txt")

    # Calculate volumes
    lv_endo_vol = biv.lv_endo_volume()
    lv_epi_vol = biv.lv_epi_volume()
    rv_endo_vol = biv.rv_endo_volume()
    rv_epi_vol = biv.rv_epi_volume()

    # Calculate mass
    lv_mass = biv.lv_mass()
    rv_mass = biv.rv_mass()

    print(f"LV Volume: {lv_endo_vol:.2f} ml")
    print(f"LV Mass: {lv_mass:.2f} g")

Working with Multiple Frames
-----------------------------

Load and analyze a sequence of cardiac frames::

    from biv_lite import BivFrames
    import matplotlib.pyplot as plt

    # Load all frames from a folder
    bivs = BivFrames.from_folder('tests/sample_frames/')

    print(f"Number of frames: {len(bivs)}")

    # Compute volumes for all frames
    volumes = bivs.volumes()

    # Plot volume curves
    plt.plot(volumes['LV_ENDO'], label='LV Volume')
    plt.plot(volumes['RV_ENDO'], label='RV Volume')
    plt.xlabel('Frame')
    plt.ylabel('Volume (ml)')
    plt.legend()
    plt.show()

Interpolating Between Frames
-----------------------------

Create smooth interpolations for continuous cardiac motion::

    from biv_lite import BivFrames, BivParametric
    import numpy as np

    # Load original frames
    bivs = BivFrames.from_folder('tests/sample_frames/')

    # Create parametric interpolator
    biv_param = BivParametric(bivs)

    # Generate interpolated frames (0.0 to 1.0)
    time_points = np.linspace(0, 1.0, 100)
    time_points = time_points[:-1]

    interpolated = biv_param(time_points)
    print(f"Interpolated to {len(interpolated)} frames")

Interactive Visualization
--------------------------

Visualize meshes interactively with PyVista::

    from biv_lite import BivFrames, BivMotionUI

    bivs = BivFrames.from_folder('tests/sample_frames/')
    ui = BivMotionUI(bivs)
    ui.plotter.show()

Command-Line Tools
-------------------

Use the ``biv-lite`` command for quick operations::

Load and inspect model

.. code-block:: bash

    $ biv-lite load tests/fitted_model.txt

Plot surface points

.. code-block:: bash

    $ biv-lite plot points tests/fitted_model.txt

Plot mesh

.. code-block:: bash

    $ biv-lite plot mesh tests/fitted_model.txt

Plot biventricular meshes

.. code-block:: bash

    $ biv-lite plot biv tests/fitted_model.txt

Calculate volumes and mass

.. code-block:: bash

    $ biv-lite volumes tests/fitted_model.txt

Next Steps
----------

- See :doc:`../api/modules` for complete API documentation
- Check the `GitHub repository <https://github.com/avansp/biv-lite>`_ for examples
- Browse the `Jupyter notebooks <https://github.com/avansp/biv-lite/tree/main/notebooks>`_ for more advanced usage
