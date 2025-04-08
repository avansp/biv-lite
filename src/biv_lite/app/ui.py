import typer
from pathlib import Path
from biv_lite.meshing.biv_motion_ui import BivMotionUI, SetVisibilityCallback
from biv_lite import BivFrames, BivMesh
import pyvista as pv
from biv_lite.meshing.vis import plot_biv_mesh

app = typer.Typer(help="User interactive biv-lite application")

@app.command(name="ui")
def start_ui(input_path: Path = typer.Argument(..., help="Either a fitted model or a folder.")):
    """Start the UI application."""
    if input_path.is_file():

        biv = BivMesh.from_fitted_model(input_path)
        p = pv.Plotter()
        actors = plot_biv_mesh(biv, p)

        size = 20
        start_pos = 10

        for lbl, a in actors.items():
            callback = SetVisibilityCallback(a)
            p.add_checkbox_button_widget(
                callback=callback,
                value=True,
                color_on=a.prop.color,
                color_off='white',
                size=size,
                border_size=1,
                position=(5.0, start_pos)
            )
            p.add_text(text=lbl, position=(30, start_pos), font_size=10)
            start_pos += size + (size // 10)
        p.show()

    elif input_path.is_dir():
        """Start UI for multiple frames of biv models"""
        biv_frames = BivFrames.from_folder(input_path)
        ui = BivMotionUI(biv_frames)
        ui.plotter.show()
    else:
        raise FileNotFoundError



