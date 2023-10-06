import typer
from loguru import logger
from pathlib import Path
import matplotlib.pyplot as plt
from biv_model_io import load_fitted_model

app = typer.Typer(help="Plot commands")


@app.command(name="points")
def plot_points(input_file: Path = typer.Argument(..., help="A fitted model control points (text file)")):
    """Quick plot of points in 3D"""
    logger.info(f"Plotting surface of {input_file}")

    # read the model
    dm = load_fitted_model(input_file)
    nodes = dm['mesh'].nodes

    ax = plt.figure().add_subplot(projection='3d')
    ax.scatter(nodes[:, 0], nodes[:, 1], nodes[:, 2], c='firebrick', marker='.')

    plt.show()
