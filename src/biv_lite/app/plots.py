import typer
from loguru import logger
from pathlib import Path
import pyvista as pv
from biv_lite import BivMesh
from biv_lite.app.vis import to_pyvista_faces, plot_biv_mesh


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
    mesh = pv.PolyData(biv.nodes, to_pyvista_faces(biv.elements))
    mesh.plot()

@app.command(name="biv")
def plot_biv(input_file: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False,
                                                help="A fitted model control points (text file)")):
    """Plot a complete biventricular model"""
    # read the model
    biv = BivMesh.from_fitted_model(input_file)
    pl = pv.Plotter()
    plot_biv_mesh(biv, pl)
    pl.show()
