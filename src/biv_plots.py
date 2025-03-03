import typer
from loguru import logger
from pathlib import Path
from biv_io import load_fitted_model
import pyvista as pv
import numpy as np


app = typer.Typer(help="Plot commands")

@app.command(name="points")
def plot_points(input_file: Path = typer.Argument(..., help="A fitted model control points (text file)")):
    """Quick plot of a model as cloud of points"""
    logger.info(f"Input file: {input_file}")

    # read the model
    dm = load_fitted_model(input_file)
    pd = pv.PolyData(dm["mesh"].nodes)
    pd.plot(point_size=5, style="points", color="dodgerblue")

@app.command(name="mesh")
def plot_mesh(input_file: Path = typer.Argument(..., help="A fitted model control points (text file)")):
    """Quick plot of a model as a surface mesh"""
    # read the model
    dm = load_fitted_model(input_file)

    # using pyvista format, you have to add number of points for each element
    faces = np.hstack([np.ones((dm["mesh"].nb_elements, 1)) * 3, dm["mesh"].elements]).astype(np.int32)

    mesh = pv.PolyData(dm["mesh"].nodes, faces)
    mesh.plot()



