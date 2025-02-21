import typer
from loguru import logger
from pathlib import Path
from biv_model_io import load_fitted_model
import plotly.express as px
import plotly.graph_objects as go

app = typer.Typer(help="Plot commands")


@app.command(name="points")
def plot_points(input_file: Path = typer.Argument(..., help="A fitted model control points (text file)")):
    """Quick plot of points in 3D"""
    logger.info(f"Input file: {input_file}")

    # read the model
    dm = load_fitted_model(input_file)
    nodes = dm['mesh'].nodes

    fig = px.scatter_3d(x=nodes[:, 0], y=nodes[:, 1], z=nodes[:, 2])
    fig.show()


@app.command(name="mesh")
def plot_mesh(input_file: Path = typer.Argument(..., help="A fitted model control points (text file)")):
    """Just to test using plotly"""
    # read the model
    dm = load_fitted_model(input_file)
    nodes = dm['mesh'].nodes

    fig = go.Figure(data=[go.Mesh3d(x=nodes[:, 0], y=nodes[:, 1], z=nodes[:, 2], opacity=0.5)])
    fig.show()
