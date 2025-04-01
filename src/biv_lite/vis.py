from biv_lite import BivMesh, Components
from biv_lite.utils import to_pyvista_faces
import pyvista as pv


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
