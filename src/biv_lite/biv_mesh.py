from biv_lite.meshing.mesh import Mesh
import numpy as np
import inspect
from pathlib import Path
from enum import IntEnum
import scipy
from biv_lite.meshing.utils import flip_elements


# component list
class Components(IntEnum):
    AORTA_VALVE = 0
    AORTA_VALVE_CUT = 1
    LV_ENDOCARDIAL = 2
    LV_EPICARDIAL = 3
    MITRAL_VALVE = 4
    MITRAL_VALVE_CUT = 5
    PULMONARY_VALVE = 6
    PULMONARY_VALVE_CUT = 7
    RV_EPICARDIAL = 8
    RV_FREEWALL = 9
    RV_SEPTUM = 10
    TRICUSPID_VALVE = 11
    TRICUSPID_VALVE_CUT = 12
    THRU_WALL = 13


class BivMesh(Mesh):
    """
    Wrap Mesh class to make it easier to work with as a biventricular model.
    """
    DEFAULT_MODEL_FOLDER = Path(inspect.getabsfile(inspect.currentframe())).parent / "model"

    def __init__(self, control_points, name: str = "biv_mesh", model_folder: Path = DEFAULT_MODEL_FOLDER):
        super().__init__(name)

        self.control_points = control_points
        self.model_folder = model_folder
        assert self.model_folder.is_dir(), f"{self.model_folder} does not exist"

        # load the Biventricular template model
        self.subdiv_matrix, vertices, elements, materials = self.load_template_model(self.model_folder)

        # create the model
        self.set_nodes(vertices)
        self.set_elements(elements)
        self.set_materials(materials[:, 0], materials[:, 1])

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(control_points={self.control_points.shape}, name={self.label})"

    def __str__(self) -> str:
        return "<BivMesh> object\n  " + "\n  ".join([
            f"Label: {self.label}",
            f"Control points: {self.control_points.shape}, dtype: {self.control_points.dtype}",
            f"Vertices: {self.nodes.shape}, dtype: {self.nodes.dtype}",
            f"Faces: {self.elements.shape}, dtype: {self.elements.dtype}",
            f"Components: {', '.join([dir(Components)[int(i)] for i in np.unique(self.materials)])}"
        ])

    def load_template_model(self, model_folder: Path):
        """Load the biventricular template model and prepare the elements & materials"""
        # read necessary files

        subdivision_matrix_file = model_folder / 'subdivision_matrix_sparse.mat'
        assert subdivision_matrix_file.is_file(), f"Cannot find {subdivision_matrix_file} file!"
        subdivision_matrix = scipy.io.loadmat(str(subdivision_matrix_file))['S'].toarray()

        elements_file = model_folder / 'ETIndicesSorted.txt'
        assert elements_file.is_file(), f"Cannot find {elements_file} file!"
        faces = np.loadtxt(elements_file).astype(int)-1

        material_file = model_folder / 'ETIndicesMaterials.txt'
        assert material_file.is_file(), f"Cannot find {material_file} file!"
        mat = np.loadtxt(material_file, dtype='str')

        # A.M. :there is a gap between septum surface and the epicardial
        #   Which needs to be closed if the RV/LV epicardial volume is needed
        #   this gap can be closed by using the et_thru_wall facets
        thru_wall_file = model_folder / 'thru_wall_et_indices.txt'
        assert thru_wall_file.is_file(), f"Cannot find {thru_wall_file} file!"
        et_thru_wall = np.loadtxt(thru_wall_file, delimiter='\t').astype(int)-1

        ## convert labels to integer corresponding to the sorted list
        # of unique labels types
        unique_material = np.unique(mat[:,1])

        materials = np.zeros(mat.shape)
        for index, m in enumerate(unique_material):
            face_index = mat[:, 1] == m
            materials[face_index, 0] = mat[face_index, 0].astype(int)
            materials[face_index, 1] = [index] * np.sum(face_index)

        # add material for the new facets
        new_elem_mat = [list(range(materials.shape[0], materials.shape[0] + et_thru_wall.shape[0])),
                        [len(unique_material)] * len(et_thru_wall)]

        vertices = np.dot(subdivision_matrix, self.control_points)
        elements = np.concatenate((faces.astype(int), et_thru_wall))
        materials = np.concatenate((materials.T, new_elem_mat), axis=1).T.astype(int)

        return subdivision_matrix, vertices, elements, materials

    @classmethod
    def from_fitted_model(cls, model_file: str | Path, **kwargs):
        """Load fitted model and returns BivMesh object."""
        # read the control points
        control_points = np.loadtxt(model_file, delimiter=',',skiprows=1, usecols=[0,1,2]).astype(float)

        return BivMesh(control_points, **kwargs)

    def lv_endo(self, open_valve = True) -> Mesh:
        """Return the LV endocardial mesh"""
        lv_comps = [Components.LV_ENDOCARDIAL]
        if not open_valve:
            lv_comps +=  [Components.AORTA_VALVE, Components.MITRAL_VALVE]

        return self.get_mesh_component(lv_comps, label="LV_ENDO", reindex_nodes=False)

    def rv_endo(self, open_valve = True) -> Mesh:
        """Return the RV endocardial mesh"""
        rv_comps = [Components.RV_FREEWALL, Components.RV_SEPTUM]
        if not open_valve:
            rv_comps += [Components.PULMONARY_VALVE, Components.TRICUSPID_VALVE]

        return self.get_mesh_component(rv_comps, label="RV_ENDO", reindex_nodes=False)

    def rvlv_epi(self, open_valve = True) -> Mesh:
        """Return the LV-RV epicardial mesh"""
        comps = [Components.LV_EPICARDIAL, Components.RV_EPICARDIAL]
        if not open_valve:
            comps += [Components.AORTA_VALVE, Components.AORTA_VALVE_CUT,
                      Components.MITRAL_VALVE, Components.MITRAL_VALVE_CUT,
                      Components.PULMONARY_VALVE, Components.PULMONARY_VALVE_CUT,
                      Components.TRICUSPID_VALVE, Components.TRICUSPID_VALVE_CUT]

        return self.get_mesh_component(comps, label="RVLV_EPI", reindex_nodes=False)

    def lv_epi(self, open_valve = True) -> Mesh:
        """Return the LV epicardial mesh"""
        comps = [Components.LV_EPICARDIAL, Components.RV_SEPTUM, Components.THRU_WALL]
        if not open_valve:
            comps += [Components.AORTA_VALVE, Components.AORTA_VALVE_CUT,
                      Components.MITRAL_VALVE, Components.MITRAL_VALVE_CUT]

        return self.get_mesh_component(comps, label="LV_EPI", reindex_nodes=False)

    def rv_epi(self, open_valve = True) -> Mesh:
        """Return the RV epicardial mesh"""
        # [6, 7, 8, 10, 11, 12, 13]
        comps = [Components.RV_EPICARDIAL, Components.RV_SEPTUM, Components.THRU_WALL]
        if not open_valve:
            comps += [Components.PULMONARY_VALVE, Components.PULMONARY_VALVE_CUT,
                      Components.TRICUSPID_VALVE, Components.TRICUSPID_VALVE_CUT]

        return self.get_mesh_component(comps, label="RV_EPI", reindex_nodes=False)

    def lv_endo_volume(self) -> float:
        """Return the LV endocardial volume"""
        return self.lv_endo(open_valve=False).get_volume().item()

    def rv_endo_volume(self) -> float:
        """Return the RV endocardial volume"""
        # need to flip normals of the RV septum
        rv_endo = self.rv_endo(open_valve=False)
        rv_endo = flip_elements(rv_endo, Components.RV_SEPTUM)

        return rv_endo.get_volume().item()

    def lv_epi_volume(self) -> float:
        """Return the LV epicardial volume"""
        # need to flip normals of the through wall elements
        lv_epi = self.lv_epi(open_valve=False)
        lv_epi = flip_elements(lv_epi, Components.THRU_WALL)

        return lv_epi.get_volume().item()

    def rv_epi_volume(self) -> float:
        """Return the RV epicardial volume"""
        # need to flip normals of the septum
        rv_epi = self.rv_epi(open_valve=False)
        rv_epi = flip_elements(rv_epi, Components.RV_SEPTUM)

        return rv_epi.get_volume().item()


