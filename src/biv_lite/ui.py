import typer
from pathlib import Path
import pyvista as pv
from biv_lite.biv_mesh import BivMesh
from biv_lite.vis import plot_biv_mesh

app = typer.Typer(help="User interactive biv-lite application")

@app.command(name="ui")
def start_ui(input_path: Path = typer.Argument(..., help="Either a fitted model or a folder.")):
    """Start the UI application."""
    if input_path.is_file():
        ui_biv_mesh(input_path)
    elif input_path.is_dir():
        raise NotImplementedError
    else:
        raise FileNotFoundError

class SetVisibilityCallback:
    """Helper callback to keep a reference to the actor being modified."""

    def __init__(self, actor) -> None:
        self.actor = actor

    def __call__(self, state):
        self.actor.SetVisibility(state)

def ui_biv_mesh(input_path: Path):
    """Start UI for a single biv model."""
    biv = BivMesh.from_fitted_model(input_path)
    p = pv.Plotter()
    actors = plot_biv_mesh(biv, p)

    size = 20
    start_pos = 10

    for lbl, a in actors.items():
        callback = SetVisibilityCallback(a)
        p.add_checkbox_button_widget(
            callback = callback,
            value = True,
            color_on = a.prop.color,
            color_off = 'white',
            size = size,
            border_size = 1,
            position = (5.0, start_pos)
        )
        p.add_text(text=lbl, position=(30, start_pos), font_size=10)
        start_pos += size + (size // 10)
    p.show()
