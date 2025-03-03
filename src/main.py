import typer
from pathlib import Path
from loguru import logger
from biv_io import load_fitted_model, DEFAULT_MODEL_FOLDER
import rich
import biv_plots

app = typer.Typer(add_completion=False,
                  help="Simple tools to load, visualise, and temporal filter biventricular models.")
app.add_typer(biv_plots.app, name="plot")

@app.command(name="load")
def load_model(input_model: Path = typer.Argument(..., help="A model txt filename."),
               model_folder: Path = typer.Option(DEFAULT_MODEL_FOLDER, help="Set the model folder."),
               model_name: str = typer.Option('Mesh', "-n", "--name", help="Set the model name.")):
    """Loads a fitted model and prints the model's data structure."""
    logger.info(f"Input model file: {input_model}")

    # load the model
    dm = load_fitted_model(input_model, model_folder, name=model_name)

    # print the information
    rich.print(f"There are {dm['control_points'].shape[0]} control points")

    # print the mesh structure
    rich.print(f"After subdivision, here is the mesh structure:")
    model = dm['mesh']
    rich.print({
        'name': model.label,
        'number_of_nodes': model.nb_nodes,
        'node_basis': model.nodes_basis,
        'nodes': [model.nodes.shape, model.nodes.dtype],
        'number_of_elements': model.nb_elements,
        'elements': [model.elements.shape, model.elements.dtype],
        'materials': [model.materials.shape, model.materials.dtype]
    })


if __name__ == "__main__":
    app()
