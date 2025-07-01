import pyvista as pv
from biv_lite.meshing.vis import plot_biv_mesh, to_pyvista_faces
from biv_lite.biv_frames import BivFrames


class BivMotionUI:
    """
    A visualization tool for rendering and interacting with Biventricular (BivMesh) models.

    This class provides an interactive user interface to visualize 3D datasets containing
    biventricular heart models. It enables the user to explore different frames of the
    model using a slider widget and provides tools to toggle the visibility of individual
    components. The visualization is built upon PyVista, and the customizable interface
    supports additional configurations for enhanced usability.

    Attributes:
        biv_frames (BivFrames): A collection or sequence of frames containing the 3D
            heart model data to be visualized.
        plotter (pv.Plotter): The PyVista plotter instance used for rendering the
            visualization.
        current_frame (int): The index of the currently displayed frame in the
            visualization.
        actors (dict): A dictionary mapping component labels (e.g., "LV", "RV", "EPI") to
            their respective 3D actors in the visualization.
        slider: The slider widget instance added to the plotter for frame selection.
    """
    def __init__(self, biv_frames: BivFrames, show_slider: bool = True):
        """
        Initializes a visualization tool for displaying BivMesh models using an interactive UI. This class
        sets up a plotter, renders the initial frame, and optionally adds a slider widget to switch between
        different frames of the dataset.

        Args:
            biv_frames: A collection or sequence of BivFrames to visualize.
            show_slider: A boolean indicating whether to display a slider widget for frame selection. Defaults to True.
        """
        self.biv_frames = biv_frames
        self.plotter = pv.Plotter()

        self.current_frame = 0
        self.actors = plot_biv_mesh(self.biv_frames[self.current_frame], self.plotter)

        if show_slider:
            self.slider = self.plotter.add_slider_widget(self.replace_mesh_callback, [0, len(self.biv_frames) - 1],
                                                         value=self.current_frame, title="Frame", fmt="%.0f")
        self.add_toggle_visibility_widgets()


    def show(self, **kwargs):
        """
        Displays the plot using the configured plotter instance.

        Args:
            **kwargs: Arbitrary keyword arguments passed to the underlying
                plotter's `show` method. These arguments allow additional
                customization or specific behavior during the rendering process.
        """
        self.plotter.show(**kwargs)


    def add_toggle_visibility_widgets(self):
        """
        Adds toggle visibility widgets to the plotter for each actor.

        This function creates widgets and text labels for toggling the visibility of
        actors in a plotter. Each actor is associated with a checkbox that allows the
        user to switch its visibility on or off. The function iterates through all the
        actors and their corresponding labels, adding these widgets to the plotter.
        """
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

    def replace_mesh_callback(self, frame_num: int):
        """
        Updates the mesh data for the current frame of a 3D heart model visualization.
        This function replaces the left ventricle (LV), right ventricle (RV), and the
        epicardium (EPI) meshes in the visualization based on the provided frame value.
        """
        if frame_num == self.current_frame:
            return

        self.current_frame = int(round(frame_num))

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


class SetVisibilityCallback:
    """
    Encapsulates a callback mechanism to set the visibility state of an actor.

    This class provides a callable object that updates the visibility state of
    a given actor. The SetVisibilityCallback object can be used to dynamically
    modify the visibility of an actor based on external inputs or events.

    Attributes:
        actor: The actor whose visibility will be controlled by the callback.
    """
    def __init__(self, actor) -> None:
        self.actor = actor

    def __call__(self, state):
        self.actor.SetVisibility(state)

