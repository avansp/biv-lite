import typer
from loguru import logger
from pathlib import Path
from biv_lite.biv_mesh import BivMesh
import rich
from typing import Dict

app = typer.Typer(add_completion=False)


@app.command(name="volumes")
def compute_volume(
        input_model: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False,
                                           help="Path to a fitted biventricular model file."),
        v2m_index: float = typer.Option(1.05, "--vol2mass", help="Index (gr/ml) to convert volume to mass"),
        silent: bool = typer.Option(False, "--silent", help="If given, no outputs are printed to the console."),
) -> Dict:
    """
    Compute and print volumes and masses.
    """
    if not silent:
        logger.info(f"Computing volumes and masses of {input_model}")

    biv = BivMesh.from_fitted_model(input_model)

    # get all volumes
    lv_endo_vol = biv.lv_endo_volume()
    rv_endo_vol = biv.rv_endo_volume()
    lv_epi_vol = biv.lv_epi_volume()
    rv_epi_vol = biv.rv_epi_volume()

    # create outputs
    vol_mass = {
        "lv_vol": lv_endo_vol,
        "rv_vol": rv_endo_vol,
        "lv_epi_vol": lv_epi_vol,
        "rv_epi_vol": rv_epi_vol,
        "lv_mass": (lv_epi_vol - lv_endo_vol) * v2m_index,
        "rv_mass": (rv_epi_vol - rv_endo_vol) * v2m_index
    }

    # print if necessary
    if not silent:
        rich.print(vol_mass)

    return vol_mass

@app.command(name="strains")
def compute_strain():
    """
    Compute and print myocardial strains

    Source: biv-me compute_global_longitudinal_strain.py file.
    """

