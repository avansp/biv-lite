from biv_lite.meshing.mesh import Mesh
import numpy as np
import inspect
from pathlib import Path
from enum import IntEnum
import scipy
from biv_lite.meshing.utils import flip_elements
import pandas as pd


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
    """Handle biventricular cardiac mesh models.

    This class extends the Mesh base class to facilitate the construction,
    manipulation, and analysis of biventricular meshes. It provides utilities
    to load fitted models, manipulate control points, and extract specific
    components (LV/RV endocardial and epicardial surfaces), with support for
    template models, subdivision matrices, and component re-indexing.

    Attributes:
        DEFAULT_MODEL_FOLDER (Path): Default folder path for model templates.
        control_points (ndarray): Control points defining the biventricular model.
        model_folder (Path): Path to the template model folder.
        subdiv_matrix (ndarray): Precomputed subdivision matrix for mesh generation.
        ls_points (DataFrame): Longitudinal strain point indices.
        cs_points (DataFrame): Circumferential strain point indices.
    """
    DEFAULT_MODEL_FOLDER = Path(inspect.getabsfile(inspect.currentframe())).parent / "model"

    def __init__(self, control_points: np.ndarray, name: str = "biv_mesh", 
                 model_folder: Path = DEFAULT_MODEL_FOLDER) -> None:
        """Initialize a biventricular mesh model.

        Creates a BivMesh instance using control points and loads necessary data
        from a template model folder to construct vertices, elements, and materials.

        Args:
            control_points: Array of control points (Nx3) for the biventricular model.
            name: Name assigned to the mesh. Defaults to "biv_mesh".
            model_folder: Path to folder containing template model data.
                Defaults to DEFAULT_MODEL_FOLDER.

        Raises:
            AssertionError: If model_folder does not exist.
        """
        super().__init__(name)

        self.control_points = control_points
        self.model_folder = model_folder
        assert self.model_folder.is_dir(), f"{self.model_folder} does not exist"

        # load the Biventricular template model
        self.subdiv_matrix, vertices, elements, materials = self.load_template_model(self.model_folder)

        # load longitudinal & circumferential strain points
        self.ls_points = pd.read_table(self.model_folder / 'ls_points.txt', sep='\t')
        self.cs_points = pd.read_table(self.model_folder / 'cs_points.txt', sep='\t')

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

    def is_empty(self):
        return self.control_points.shape[0] == 0

    def load_template_model(self, model_folder: Path) -> tuple:
        """Load template model files from the specified folder.

        Reads mesh data including subdivision matrix, elements, and material
        information from model files.

        Args:
            model_folder: Path to folder containing template model files.

        Returns:
            A tuple containing:
                - subdivision_matrix (ndarray): Subdivision matrix (sparse).
                - vertices (ndarray): Mesh vertices/nodes.
                - elements (ndarray): Triangle element connectivity.
                - materials (ndarray): Material identifiers for elements.

        Raises:
            AssertionError: If required model files are not found.
        """
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

        if not self.is_empty():
            vertices = np.dot(subdivision_matrix, self.control_points)
        else:
            vertices = np.empty((0, 3))

        elements = np.concatenate((faces.astype(int), et_thru_wall))
        materials = np.concatenate((materials.T, new_elem_mat), axis=1).T.astype(int)

        return subdivision_matrix, vertices, elements, materials

    @classmethod
    def from_fitted_model(cls, model_file: str | Path, **kwargs) -> 'BivMesh':
        """Create a BivMesh from a fitted model file.

        Loads control points from a comma-separated file (3 columns: x, y, z)
        and initializes a BivMesh object.

        Args:
            model_file: Path to the fitted model file (CSV format with control points
                in columns 0-2).
            **kwargs: Additional keyword arguments passed to BivMesh constructor.

        Returns:
            A new BivMesh instance initialized with loaded control points.
        """
        # read the control points
        control_points = np.loadtxt(model_file, delimiter=',',skiprows=1, usecols=[0,1,2]).astype(float)

        return BivMesh(control_points, **kwargs)

    def to_fitted_model(self, model_file: str | Path, frame_num: int) -> None:
        """Write model control points to a fitted model file.

        Args:
            model_file: Output file path for the fitted model.
            frame_num: Frame number to write in the output file.
        """
        np.savetxt(
            model_file,
            np.c_[self.control_points, frame_num * np.ones(self.control_points.shape[0])],
            fmt=['%.16f', '%.16f', '%.16f', '%d'],
            delimiter=',',
            header="x,y,z,Frame",
            comments=""
        )

    def lv_endo(self, open_valve: bool = True) -> Mesh:
        """Get left ventricular endocardial mesh.

        Args:
            open_valve: If True, exclude aortic and mitral valves.
                Defaults to True.

        Returns:
            Mesh object representing the LV endocardium.
        """
        lv_comps = [Components.LV_ENDOCARDIAL]
        if not open_valve:
            lv_comps +=  [Components.AORTA_VALVE, Components.MITRAL_VALVE]

        return self.get_mesh_component(lv_comps, label="LV_ENDO", reindex_nodes=False)

    def rv_endo(self, open_valve: bool = True) -> Mesh:
        """Get right ventricular endocardial mesh.

        Args:
            open_valve: If True, exclude pulmonary and tricuspid valves.
                Defaults to True.

        Returns:
            Mesh object representing the RV endocardium.
        """
        rv_comps = [Components.RV_FREEWALL, Components.RV_SEPTUM]
        if not open_valve:
            rv_comps += [Components.PULMONARY_VALVE, Components.TRICUSPID_VALVE]

        return self.get_mesh_component(rv_comps, label="RV_ENDO", reindex_nodes=False)

    def rvlv_epi(self, open_valve: bool = True) -> Mesh:
        """Get epicardial mesh for both ventricles.

        Args:
            open_valve: If True, exclude valve structures. If False, include
                aortic, mitral, pulmonary, and tricuspid valves with cuts.
                Defaults to True.

        Returns:
            Mesh object representing RV and LV epicardial surfaces.
        """
        comps = [Components.LV_EPICARDIAL, Components.RV_EPICARDIAL]
        if not open_valve:
            comps += [Components.AORTA_VALVE, Components.AORTA_VALVE_CUT,
                      Components.MITRAL_VALVE, Components.MITRAL_VALVE_CUT,
                      Components.PULMONARY_VALVE, Components.PULMONARY_VALVE_CUT,
                      Components.TRICUSPID_VALVE, Components.TRICUSPID_VALVE_CUT]

        return self.get_mesh_component(comps, label="RVLV_EPI", reindex_nodes=False)

    def lv_epi(self, open_valve: bool = True) -> Mesh:
        """Get left ventricular epicardial mesh.

        Args:
            open_valve: If True, exclude aortic and mitral valves with cuts.
                Defaults to True.

        Returns:
            Mesh object representing LV epicardium.
        """
        comps = [Components.LV_EPICARDIAL, Components.RV_SEPTUM, Components.THRU_WALL]
        if not open_valve:
            comps += [Components.AORTA_VALVE, Components.AORTA_VALVE_CUT,
                      Components.MITRAL_VALVE, Components.MITRAL_VALVE_CUT]

        return self.get_mesh_component(comps, label="LV_EPI", reindex_nodes=False)

    def rv_epi(self, open_valve: bool = True) -> Mesh:
        """Get right ventricular epicardial mesh.

        Args:
            open_valve: If True, exclude pulmonary and tricuspid valves with cuts.
                Defaults to True.

        Returns:
            Mesh object representing RV epicardium.
        """
        # [6, 7, 8, 10, 11, 12, 13]
        comps = [Components.RV_EPICARDIAL, Components.RV_SEPTUM, Components.THRU_WALL]
        if not open_valve:
            comps += [Components.PULMONARY_VALVE, Components.PULMONARY_VALVE_CUT,
                      Components.TRICUSPID_VALVE, Components.TRICUSPID_VALVE_CUT]

        return self.get_mesh_component(comps, label="RV_EPI", reindex_nodes=False)

    def lv_endo_volume(self) -> float:
        """Calculate left ventricular endocardial volume.

        Returns:
            LV endocardial volume in ml. Returns NaN if mesh is empty.
        """
        return np.nan if self.is_empty() else self.lv_endo(open_valve=False).get_volume().item()

    def rv_endo_volume(self) -> float:
        """Calculate right ventricular endocardial volume.

        Returns:
            RV endocardial volume in ml. Returns NaN if mesh is empty.
        """
        # need to flip normals of the RV septum
        if self.is_empty():
            return np.nan

        rv_endo = self.rv_endo(open_valve=False)
        rv_endo = flip_elements(rv_endo, Components.RV_SEPTUM)

        return rv_endo.get_volume().item()

    def lv_epi_volume(self) -> float:
        """Calculate left ventricular epicardial volume.

        Returns:
            LV epicardial volume in ml. Returns NaN if mesh is empty.
        """
        if self.is_empty():
            return np.nan

        # need to flip normals of the through wall elements
        lv_epi = self.lv_epi(open_valve=False)
        lv_epi = flip_elements(lv_epi, Components.THRU_WALL)

        return lv_epi.get_volume().item()

    def rv_epi_volume(self) -> float:
        """Calculate right ventricular epicardial volume.

        Returns:
            RV epicardial volume in ml. Returns NaN if mesh is empty.
        """
        if self.is_empty():
            return np.nan

        # need to flip normals of the septum
        rv_epi = self.rv_epi(open_valve=False)
        rv_epi = flip_elements(rv_epi, Components.RV_SEPTUM)

        return rv_epi.get_volume().item()

    def lv_mass(self, mass_index: float = 1.05) -> float:
        """Calculate left ventricular mass.

        Mass is computed as (epicardial_volume - endocardial_volume) * mass_index.

        Args:
            mass_index: Scaling factor for mass calculation. Defaults to 1.05 g/ml.

        Returns:
            LV mass in grams. Returns NaN if mesh is empty.
        """
        if self.is_empty():
            return np.nan

        lv_endo_vol = self.lv_endo_volume()
        lv_epi_vol = self.lv_epi_volume()

        return mass_index * (lv_epi_vol - lv_endo_vol)

    def rv_mass(self, mass_index: float = 1.05) -> float:
        """Calculate right ventricular mass.

        Mass is computed as (epicardial_volume - endocardial_volume) * mass_index.

        Args:
            mass_index: Scaling factor for mass calculation. Defaults to 1.05 g/ml.

        Returns:
            RV mass in grams. Returns NaN if mesh is empty.
        """
        if self.is_empty():
            return np.nan

        rv_endo_vol = self.rv_endo_volume()
        rv_epi_vol = self.rv_epi_volume()

        return mass_index * (rv_epi_vol - rv_endo_vol)
    
    def long_arc_length(self, view: str, surface: str) -> float:
        """Compute longitudinal arc length along a surface.

        Used for computing longitudinal strain in BivFrames.

        Args:
            view: Either '2CH' (two-chamber) or '4CH' (four-chamber).
            surface: Either 'LV' (left ventricle), 'RVS' (RV septum),
                or 'RVFW' (RV freewall).

        Returns:
            Longitudinal arc length in mm. Returns NaN if mesh is empty.
        """
        if self.is_empty():
            return np.nan
        
        vertices = self.nodes[(self.ls_points[(self.ls_points.View == view) & (self.ls_points.Surface == surface)].Index).to_numpy(), :]
        return np.linalg.norm(vertices[1:, ] - vertices[:-1, ], axis=1).sum().item()

    def circ_arc_length(self, slice: str, surface: str) -> float:
        """Compute circumferential arc length along a surface.

        Used for computing circumferential strain in BivFrames.

        Args:
            slice: Either 'APEX', 'MID' (mid-ventricular), or 'BASE'.
            surface: Either 'LV' (left ventricle), 'RVS' (RV septum),
                or 'RVFW' (RV freewall).

        Returns:
            Circumferential arc length in mm. Returns NaN if mesh is empty.
        """
        if self.is_empty():
            return np.nan
        
        vertices = self.nodes[(self.cs_points[(self.cs_points.View == slice) & (self.cs_points.Surface == surface)].Index).to_numpy(), :]
        return np.linalg.norm(vertices[1:, ] - vertices[:-1, ], axis=1).sum().item()
