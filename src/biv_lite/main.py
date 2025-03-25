import typer
from pathlib import Path
from loguru import logger
from biv_lite.biv_mesh import BivMesh
import rich
import biv_lite.measures as bm
import biv_lite.plots as bp

app = typer.Typer(add_completion=False,
                  help="Simple tools to load, visualise, and temporal filter biventricular models.")
app.add_typer(bp.app, name="plot")
app.add_typer(bm.app)


@app.command(name="load")
def load_model(input_model: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False,
                                                  help="A model txt filename."),
               model_folder: Path = typer.Option(BivMesh.DEFAULT_MODEL_FOLDER, exists=True, file_okay=False,
                                                 dir_okay=True, help="Set the model folder."),
               model_name: str = typer.Option('Mesh', "-n", "--name", help="Set the model name.")):
    """Loads a fitted model and prints the model's data structure."""
    logger.info(f"Input model file: {input_model}")

    # load the model
    model = BivMesh.from_fitted_model(input_model, name = model_name, model_folder = model_folder)

    # print the information
    rich.print(f"There are {model.control_points.shape[0]} control points")

    # print the mesh structure
    rich.print(f"After subdivision, here is the mesh structure:")
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
