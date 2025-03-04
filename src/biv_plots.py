import typer
from loguru import logger
from pathlib import Path
import pyvista as pv
import numpy as np
from biv_mesh import BivMesh


app = typer.Typer(help="Plot commands")

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

    # using pyvista format, you have to add number of points for each element
    faces = np.hstack([np.ones((biv.nb_elements, 1)) * 3, biv.elements]).astype(np.int32)

    mesh = pv.PolyData(biv.nodes, faces)
    mesh.plot()



