import typer
from loguru import logger
from pathlib import Path
from biv_mesh import BivMesh

app = typer.Typer(add_completion=False)


@app.command()
def compute_volume(
        input_model: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False,
                                           help="Path to a fitted biventricular model file.")
):
    """
    Compute the volume of a biventricular model.
    """
    logger.info(f"Computing volume of {input_model}")

    biv = BivMesh.from_fitted_model(input_model)
