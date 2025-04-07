import typer
from pathlib import Path
import pyvista as pv
from biv_lite.biv_mesh import BivMesh
from biv_lite.app.vis import plot_biv_mesh, to_pyvista_faces
from biv_lite.biv_frames import BivFrames

app = typer.Typer(help="User interactive biv-lite application")

@app.command(name="ui")
def start_ui(input_path: Path = typer.Argument(..., help="Either a fitted model or a folder.")):
    """Start the UI application."""
    if input_path.is_file():
        ui_biv_mesh(input_path)
    elif input_path.is_dir():
        ui_biv_frames(input_path)
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


def ui_biv_frames(input_path: Path):
    """Start UI for multiple frames of biv models"""
    biv_frames = BivFrames.from_folder(input_path)
    ui = BivMotionUI(biv_frames)
    ui.plotter.show()

class BivMotionUI:
    def __init__(self, biv_frames: BivFrames, show_slider: bool = True):
        self.biv_frames = biv_frames
        self.plotter = pv.Plotter()

        self.current_frame = 0
        self.actors = plot_biv_mesh(self.biv_frames[self.current_frame], self.plotter)

        if show_slider:
            self.slider = self.plotter.add_slider_widget(self.replace_mesh_callback, [0, len(self.biv_frames) - 1],
                                                         value=self.current_frame, title="Frame", fmt="%.0f")
        self.add_toggle_visibility_widgets()


    def add_toggle_visibility_widgets(self):
        size = 20
        start_pos = 10

        for lbl, a in self.actors.items():
            toggle_vis_callback = SetVisibilityCallback(a)
            self.plotter.add_checkbox_button_widget(
                callback=toggle_vis_callback,
                value=True,
                color_on=a.prop.color,
                color_off='white',
                size=size,
                border_size=1,
                position=(5.0, start_pos)
            )
            self.plotter.add_text(text=lbl, position=(30, start_pos), font_size=10)
            start_pos += size + (size // 10)

    def replace_mesh_callback(self, value):
        if int(round(value)) == self.current_frame:
            return

        self.current_frame = int(round(value))

        # replace LV
        lv = self.biv_frames[self.current_frame].lv_endo()
        mesh = pv.PolyData(lv.nodes, to_pyvista_faces(lv.elements))
        self.actors['LV'].mapper.dataset.copy_from(mesh)

        # replace RV
        rv = self.biv_frames[self.current_frame].rv_endo()
        mesh = pv.PolyData(rv.nodes, to_pyvista_faces(rv.elements))
        self.actors['RV'].mapper.dataset.copy_from(mesh)

        # replace EPI
        epi = self.biv_frames[self.current_frame].rvlv_epi()
        mesh = pv.PolyData(epi.nodes, to_pyvista_faces(epi.elements))
        self.actors['EPI'].mapper.dataset.copy_from(mesh)

