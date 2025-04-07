from biv_lite import BivMesh, Components
import pyvista as pv
import numpy as np


# using pyvista format, you have to add number of points for each element
def to_pyvista_faces(elements: np.ndarray) -> np.ndarray:
    return np.hstack([np.ones((elements.shape[0], 1)) * 3, elements]).astype(np.int32)


def plot_biv_mesh(biv: BivMesh, pl: pv.Plotter):
    """Plot a default biventricular model"""
    lv = biv.lv_endo()
    lv_actor = pl.add_mesh(pv.PolyData(lv.nodes, to_pyvista_faces(lv.elements)), color="firebrick", opacity="linear", line_width=True)

    rv = biv.rv_endo()
    rv_actor = pl.add_mesh(pv.PolyData(rv.nodes, to_pyvista_faces(rv.elements)), color="dodgerblue", opacity="linear", line_width=True)

    epi = biv.rvlv_epi()
    epi_actor = pl.add_mesh(pv.PolyData(epi.nodes, to_pyvista_faces(epi.elements)), color="green", opacity=0.6, line_width=True)

    return {
        'LV': lv_actor,
        'RV': rv_actor,
        'EPI': epi_actor
    }

