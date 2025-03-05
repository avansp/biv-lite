import typer
from loguru import logger
from pathlib import Path
import pyvista as pv
import numpy as np
from biv_mesh import BivMesh


app = typer.Typer(help="Plot commands")

# using pyvista format, you have to add number of points for each element
def to_pyvista_faces(elements: np.ndarray) -> np.ndarray:
    return np.hstack([np.ones((elements.shape[0], 1)) * 3, elements]).astype(np.int32)

@app.command(name="points")
def plot_points(input_file: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False,
                                                  help="A fitted model control points (text file)")):
    """Quick plot of a model as cloud of points"""
    logger.info(f"Input file: {input_file}")

    # read the model
    biv = BivMesh.from_fitted_model(input_file)
    pv.PolyData(biv.nodes).plot(point_size=5, style="points", color="dodgerblue")


@app.command(name="mesh")
def plot_mesh(input_file: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False,
                                                help="A fitted model control points (text file)")):
    """Quick plot of a model as a surface mesh"""
    # read the model
    biv = BivMesh.from_fitted_model(input_file)
    mesh = pv.PolyData(biv.nodes, to_pyvista_faces(biv.elements))
    mesh.plot()


@app.command(name="biv")
def plot_biv(input_file: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False,
                                                help="A fitted model control points (text file)")):
    """Plot a complete biventricular model"""
    # read the model
    biv = BivMesh.from_fitted_model(input_file)

    pl = pv.Plotter()

    lv = biv.lv_endo()
    pl.add_mesh(pv.PolyData(lv.nodes, to_pyvista_faces(lv.elements)), color="firebrick", opacity="linear", line_width=True)

    rv = biv.rv_endo()
    pl.add_mesh(pv.PolyData(rv.nodes, to_pyvista_faces(rv.elements)), color="dodgerblue", opacity="linear", line_width=True)

    epi = biv.lvrv_epi()
    pl.add_mesh(pv.PolyData(epi.nodes, to_pyvista_faces(epi.elements)), color="green", opacity=0.6, line_width=True)

    pl.show()
