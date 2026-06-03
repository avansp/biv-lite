"""Visualization helpers for bi-ventricular meshes using PyVista.

This module provides helper functions to convert mesh element arrays into
PyVista-compatible face arrays and to plot or replace biventricular mesh
components with sensible default styling.
"""

from biv_lite import BivMesh
import pyvista as pv
import numpy as np


_DEFAULT_LV = {"color":"firebrick", "style":'surface', "opacity":0.6, "line_width":True}
_DEFAULT_RV = {"color":"dodgerblue", "style":'surface', "opacity":0.6, "line_width":True}
_DEFAULT_EPI = {"color":"darkgray", "style":"wireframe", "opacity":0.5, "line_width":True}


# using pyvista format, you have to add number of points for each element
def to_pyvista_faces(elements: np.ndarray) -> np.ndarray:
    """Convert element array to PyVista face format.
    
    Prepends the number of points (3) for each triangular element to comply with
    PyVista's face definition format.
    
    :param elements: Array of shape (n, 3) containing triangle vertex indices
    :type elements: np.ndarray
    :return: Array of shape (n, 4) with face format [3, i, j, k] for each triangle
    :rtype: np.ndarray
    """
    return np.hstack([np.ones((elements.shape[0], 1)) * 3, elements]).astype(np.int32)


def plot_mesh(mesh: BivMesh, pl: pv.Plotter, **kwargs) -> pv.Actor:
    """Plot a single mesh on a PyVista plotter.

    :param mesh: Mesh to plot.
    :type mesh: BivMesh
    :param pl: PyVista plotter instance.
    :type pl: pv.Plotter
    :param kwargs: Additional keyword arguments passed to :meth:`pyvista.Plotter.add_mesh`.
    :return: Added actor.
    :rtype: pv.Actor
    """
    return pl.add_mesh(pv.PolyData(mesh.nodes, to_pyvista_faces(mesh.elements)), **kwargs)


def plot_biv_mesh(biv: BivMesh, pl: pv.Plotter, name:str = 'BiV',
                  kwargs_lv: dict = _DEFAULT_LV, kwargs_rv: dict = _DEFAULT_RV, kwargs_epi: dict = _DEFAULT_EPI):
    """Plot a default biventricular model.

    :param biv: Biventricular mesh instance.
    :type biv: BivMesh
    :param pl: PyVista plotter instance.
    :type pl: pv.Plotter
    :param name: Base name for mesh components.
    :type name: str
    :param kwargs_lv: Keyword arguments for left ventricle rendering.
    :type kwargs_lv: dict
    :param kwargs_rv: Keyword arguments for right ventricle rendering.
    :type kwargs_rv: dict
    :param kwargs_epi: Keyword arguments for epicardial surface rendering.
    :type kwargs_epi: dict
    :return: Dictionary of added actors for LV, RV, and EPI surfaces.
    :rtype: dict[str, pv.Actor]
    """
    return {
        'LV': plot_mesh(biv.lv_endo(), pl, name="-".join([name, "LV"]), **kwargs_lv),
        'RV': plot_mesh(biv.rv_endo(), pl, name="-".join([name, "RV"]), **kwargs_rv),
        'EPI': plot_mesh(biv.rvlv_epi(), pl, name="-".join([name, "EPI"]), **kwargs_epi)
    }

def replace_mesh(actor, biv):
    """Replace the visualized biventricular mesh with a new mesh.

    :param actor: Dictionary of existing actors keyed by mesh region.
    :type actor: dict[str, pv.Actor]
    :param biv: New biventricular mesh instance.
    :type biv: BivMesh
    """
    # replace LV
    lv = biv.lv_endo()
    mesh = pv.PolyData(lv.nodes, to_pyvista_faces(lv.elements))
    actor['LV'].mapper.dataset.copy_from(mesh)

    # replace RV
    rv = biv.rv_endo()
    mesh = pv.PolyData(rv.nodes, to_pyvista_faces(rv.elements))
    actor['RV'].mapper.dataset.copy_from(mesh)

    # replace EPI
    epi = biv.rvlv_epi()
    mesh = pv.PolyData(epi.nodes, to_pyvista_faces(epi.elements))
    actor['EPI'].mapper.dataset.copy_from(mesh)
