import numpy as np
import polars as pl
import pytest
from pathlib import Path

from biv_lite.biv_mesh import BivMesh


def make_bivmesh_instance():
    # Create an instance without invoking __init__ (avoid file IO)
    mesh = BivMesh.__new__(BivMesh)
    mesh.label = "test"
    return mesh


def test_set_control_points_and_nodes_size_validation():
    mesh = make_bivmesh_instance()

    valid_control_points = np.zeros((388, 3), dtype=float)
    mesh.control_points = valid_control_points
    assert np.array_equal(mesh._control_points, valid_control_points)

    invalid_control_points = np.zeros((5810, 3), dtype=float)
    with pytest.raises(ValueError):
        mesh.control_points = invalid_control_points


def test_is_empty_true():
    mesh = make_bivmesh_instance()
    # set control points directly to simulate empty mesh
    mesh._control_points = np.empty((0, 3))
    assert mesh.is_empty() is True


def test_to_fitted_model_writes_file(tmp_path: Path):
    mesh = make_bivmesh_instance()

    # create control points with expected shape (388,3)
    cp = np.linspace(0.0, 1.0, 388 * 3).reshape((388, 3))
    mesh._control_points = cp

    out = tmp_path / "fitted_model_test.csv"
    mesh.to_fitted_model(out, frame_num=5)

    # read back and verify shape and values
    data = np.loadtxt(out, delimiter=",", skiprows=1)
    assert data.shape == (388, 4)
    assert np.allclose(data[:, :3], cp)


