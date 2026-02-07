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
    """
    This class extends the Mesh base class to specifically handle biventricular cardiac models.
    The purpose of this class is to facilitate the construction, manipulation, and analysis of
    biventricular meshes. It provides utilities to load fitted models, manipulate
    control points, and extract specific components of the mesh, such as the left ventricle (LV)
    and right ventricle (RV) endocardial and epicardial surfaces. The class supports features
    such as reading template models and fitted control points, handling subdivision matrices,
    and performing re-indexing where necessary.

    Attributes:
        DEFAULT_MODEL_FOLDER (Path): The default folder path to the model templates.
        control_points: A matrix that defines the control points of the biventricular model.
        model_folder (Path): Path to the template model folder.
        subdiv_matrix: Precomputed subdivision matrix for generating mesh nodes.
    """
    DEFAULT_MODEL_FOLDER = Path(inspect.getabsfile(inspect.currentframe())).parent / "model"

    def __init__(self, control_points, name: str = "biv_mesh", model_folder: Path = DEFAULT_MODEL_FOLDER):
        """
        Represents a class responsible for initializing and creating a biventricular
        mesh model using a given set of control points. Loads necessary data from a
        specified template model folder and assigns vertices, elements, and
        materials to construct the model.

        Args:
            control_points: Control points used to construct the biventricular model.
            name: Name assigned to the model. Defaults to "biv_mesh".
            model_folder: Path to the folder containing the template model data. Defaults
                to DEFAULT_MODEL_FOLDER. Must be a valid directory.
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

    def load_template_model(self, model_folder: Path):
        """
        Loads a template model by reading necessary model files from the specified
        folder.

        Args:
            model_folder (Path): Path to the folder where fitted model files
                are stored.

        Returns:
            tuple: A tuple containing the following elements:
                - subdivision_matrix (ndarray): The subdivision matrix loaded
                  from the corresponding file.
                - vertices (ndarray): The control points matrix.
                - elements (ndarray): Mesh elements.
                - materials (ndarray): Material data for elements.
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
    def from_fitted_model(cls, model_file: str | Path, **kwargs):
        """
        Creates a BivMesh instance using a fitted model file.

        This class method loads control points from a specified model file
        and initializes a BivMesh object with the loaded data. The method
        expects the file to contain comma-separated values, with the
        control points located in the first three columns of the file.
        Additional arguments for initializing the BivMesh object may
        also be provided.

        Args:
            model_file (str | Path): Path to the file containing the model data,
                which must include control points in a comma-separated format.
            **kwargs: Additional parameters that are passed to the BivMesh
                initializer.

        Returns:
            BivMesh: A new BivMesh instance initialized with control points
            from the given model file and any additional parameters.
        """
        # read the control points
        control_points = np.loadtxt(model_file, delimiter=',',skiprows=1, usecols=[0,1,2]).astype(float)

        return BivMesh(control_points, **kwargs)

    def to_fitted_model(self, model_file: str | Path, frame_num: int) -> None:
        """Write the model control points into a text file"""
        np.savetxt(
            model_file,
            np.c_[self.control_points, frame_num * np.ones(self.control_points.shape[0])],
            fmt=['%.16f', '%.16f', '%.16f', '%d'],
            delimiter=',',
            header="x,y,z,Frame",
            comments=""
        )

    def lv_endo(self, open_valve = True) -> Mesh:
        """
        Fetch a mesh representation of the left ventricular endocardial components with the
        option to include or exclude valve structures.

        Args:
            open_valve: A boolean indicating whether to leave valve structures (AORTA_VALVE
                and MITRAL_VALVE) open or exclude them from the mesh. If True, the valves are
                not included. Defaults to True.

        Returns:
            Mesh: The mesh object representing the specified left ventricular components
            with relevant configuration based on the open_valve flag.
        """
        lv_comps = [Components.LV_ENDOCARDIAL]
        if not open_valve:
            lv_comps +=  [Components.AORTA_VALVE, Components.MITRAL_VALVE]

        return self.get_mesh_component(lv_comps, label="LV_ENDO", reindex_nodes=False)

    def rv_endo(self, open_valve = True) -> Mesh:
        """
        Generates the mesh component for the right ventricular endocardium based on the specified components.
        Optionally includes the pulmonary and tricuspid valves if `open_valve` is set to `False`.

        Args:
            open_valve (bool, optional): Determines whether to include the pulmonary and tricuspid
                valves in the generated mesh. If `True`, the valves are excluded. Defaults to `True`.

        Returns:
            Mesh: The combined mesh component for the right ventricular endocardium, including the
                specified components based on the `open_valve` argument.
        """
        rv_comps = [Components.RV_FREEWALL, Components.RV_SEPTUM]
        if not open_valve:
            rv_comps += [Components.PULMONARY_VALVE, Components.TRICUSPID_VALVE]

        return self.get_mesh_component(rv_comps, label="RV_ENDO", reindex_nodes=False)

    def rvlv_epi(self, open_valve = True) -> Mesh:
        """Retrieve the mesh component for the epicardial surfaces of the right and left ventricle,
        optionally including valves.

        This method provides a mesh that includes the epicardial components of the
        left and right ventricles. By setting the 'open_valve' parameter to False,
        additional components corresponding to various valves are included in the mesh structure.

        Args:
            open_valve (bool): If True, the valves are not included in the mesh. If False,
                components for the aortic, mitral, pulmonary, and tricuspid valves and
                their respective cut segments are included.

        Returns:
            Mesh: The constructed mesh component containing the specified elements.
        """
        comps = [Components.LV_EPICARDIAL, Components.RV_EPICARDIAL]
        if not open_valve:
            comps += [Components.AORTA_VALVE, Components.AORTA_VALVE_CUT,
                      Components.MITRAL_VALVE, Components.MITRAL_VALVE_CUT,
                      Components.PULMONARY_VALVE, Components.PULMONARY_VALVE_CUT,
                      Components.TRICUSPID_VALVE, Components.TRICUSPID_VALVE_CUT]

        return self.get_mesh_component(comps, label="RVLV_EPI", reindex_nodes=False)

    def lv_epi(self, open_valve = True) -> Mesh:
        """
        Generates and retrieves the mesh corresponding to the left ventricle epicardium (LV EPI). This includes specific
        components representing the epicardium structure. Optionally, additional valve components (aorta and mitral valves,
        along with their cut regions) can be excluded based on the parameter provided.

        Args:
            open_valve (bool): A flag to determine whether valve components, including aorta and mitral valves and their
                cuts, are included in the mesh. If True, valves are included; otherwise, they are excluded.

        Returns:
            Mesh: The resultant mesh object corresponding to the LV EPI region, potentially including or excluding valve
            components based on the `open_valve` parameter.
        """
        comps = [Components.LV_EPICARDIAL, Components.RV_SEPTUM, Components.THRU_WALL]
        if not open_valve:
            comps += [Components.AORTA_VALVE, Components.AORTA_VALVE_CUT,
                      Components.MITRAL_VALVE, Components.MITRAL_VALVE_CUT]

        return self.get_mesh_component(comps, label="LV_EPI", reindex_nodes=False)

    def rv_epi(self, open_valve = True) -> Mesh:
        """
        Extracts the mesh component for the right ventricle epicardium (RV_EPI), including
        or excluding specific valve components based on the `open_valve` flag.

        This function retrieves the mesh components for the right ventricle's epicardial
        region, including the septum and through-wall components. If the `open_valve` flag
        is set to False, it adds additional valve-related components such as the pulmonary
        and tricuspid valves, along with their associated cut regions.

        Args:
            open_valve (bool, optional): If True, excludes valve components (default is True).

        Returns:
            Mesh: A mesh object representing the requested components for RV_EPI.
        """
        # [6, 7, 8, 10, 11, 12, 13]
        comps = [Components.RV_EPICARDIAL, Components.RV_SEPTUM, Components.THRU_WALL]
        if not open_valve:
            comps += [Components.PULMONARY_VALVE, Components.PULMONARY_VALVE_CUT,
                      Components.TRICUSPID_VALVE, Components.TRICUSPID_VALVE_CUT]

        return self.get_mesh_component(comps, label="RV_EPI", reindex_nodes=False)

    def lv_endo_volume(self) -> float:
        """
        Calculates the left ventricular endocardial volume.

        This method determines the volume of the left ventricular endocardium by checking whether the structure is
        empty. If it is empty, a NaN value is returned. Otherwise, it calculates the volume using the `lv_endo`
        method with the valve in a closed state and retrieves the volume as a floating-point number.

        Returns:
            float: The calculated left ventricular endocardial volume if available, otherwise NaN.
        """
        return np.nan if self.is_empty() else self.lv_endo(open_valve=False).get_volume().item()

    def rv_endo_volume(self) -> float:
        """
        Calculates the end-diastolic volume of the right ventricle (RV) based on the
        geometry, taking into account specific modifications required to accurately
        reflect the structure.

        This method assesses whether the structure is empty, flips the normals of the
        RV septum as needed, and computes the volume of the RV endocardium.

        Returns:
            float: The computed volume of the right ventricle endocardium. Returns
            NaN if the structure is empty.
        """
        # need to flip normals of the RV septum
        if self.is_empty():
            return np.nan

        rv_endo = self.rv_endo(open_valve=False)
        rv_endo = flip_elements(rv_endo, Components.RV_SEPTUM)

        return rv_endo.get_volume().item()

    def lv_epi_volume(self) -> float:
        """
        Computes and returns the volume of the left ventricular epicardium.

        This function first verifies if the required data is available; if not,
        it returns NaN. It processes the left ventricular epicardium by
        flipping the normals of through-wall elements to ensure proper
        orientation. Finally, it calculates and returns the volume of the
        left ventricular epicardium.

        Returns:
            float: The computed volume of the left ventricular epicardium.
            Returns NaN if the required data is not available.
        """
        if self.is_empty():
            return np.nan

        # need to flip normals of the through wall elements
        lv_epi = self.lv_epi(open_valve=False)
        lv_epi = flip_elements(lv_epi, Components.THRU_WALL)

        return lv_epi.get_volume().item()

    def rv_epi_volume(self) -> float:
        """
        Calculates the volume of the right ventricle (RV) epicardium.

        This function computes the volume of the RV epicardium based on the current
        geometry configuration. If the dataset is empty, it returns NaN. Additionally,
        it accounts for flipping the normals of the septum to ensure correct volume
        calculations.

        Returns:
            float: The computed volume of the RV epicardium. Returns NaN if the
            dataset is empty.
        """
        if self.is_empty():
            return np.nan

        # need to flip normals of the septum
        rv_epi = self.rv_epi(open_valve=False)
        rv_epi = flip_elements(rv_epi, Components.RV_SEPTUM)

        return rv_epi.get_volume().item()

    def lv_mass(self, mass_index: float = 1.05) -> float:
        """
        Calculates the left ventricular (LV) mass using the difference between the
        epicardial volume and the endocardial volume, scaled by a mass index.

        This method computes the LV mass by subtracting the endocardial (inner)
        volume from the epicardial (outer) volume and then multiplying the result
        by a given mass index. If the object is empty (e.g., has no data), it will
        return 'np.nan'.

        Args:
            mass_index (float): A multiplier applied to the calculated LV mass to
                scale or adjust the mass value. Defaults to 1.05.

        Returns:
            float: The calculated LV mass. Returns 'np.nan' if the object is empty.
        """
        if self.is_empty():
            return np.nan

        lv_endo_vol = self.lv_endo_volume()
        lv_epi_vol = self.lv_epi_volume()

        return mass_index * (lv_epi_vol - lv_endo_vol)

    def rv_mass(self, mass_index: float = 1.05) -> float:
        """
        Calculates the right ventricular (RV) mass based on the endocardial and epicardial
        volumes using a specified mass index. This method returns the calculated RV mass
        or NaN if the data is unavailable.

        Args:
            mass_index (float): A multiplier used to scale the difference between the RV
                epicardial and endocardial volumes. Defaults to 1.05.

        Returns:
            float: The calculated RV mass based on the given mass index and ventricular
            volumes. Returns NaN if the RV mass cannot be computed due to empty data.
        """
        if self.is_empty():
            return np.nan

        rv_endo_vol = self.rv_endo_volume()
        rv_epi_vol = self.rv_epi_volume()

        return mass_index * (rv_epi_vol - rv_endo_vol)
    
    def long_arc_length(self, view: str, surface: str) -> float:
        """
        Compute longitudinal arc length along the surface. It's needed to compute BivFrames' longitudinal strain values.

        Args:
            view (str): is either '2CH' or '4CH'.
            surface (str): is either 'LV', 'RVS', or 'RVFW.

        Returns:
            float: the arc length acros the given view on the given surface.
        """
        if self.is_empty():
            return np.nan
        
        vertices = self.nodes[(self.ls_points[(self.ls_points.View == view) & (self.ls_points.Surface == surface)].Index).to_numpy(), :]
        return np.linalg.norm(vertices[1:, ] - vertices[:-1, ], axis=1).sum().item()

    def circ_arc_length(self, slice: str, surface: str) -> float:
        """
        Compute circumferential arc length along the surface. It's needed to compute BivFrames' circumferential strain values.

        Args:
            slice (str): is either 'APEX', 'MID', or 'BASE'
            surface (str): is either 'LV', 'RVS', or 'RVFW.

        Returns:
            float: the arc length acros the given view on the given surface.
        """
        if self.is_empty():
            return np.nan
        
        vertices = self.nodes[(self.cs_points[(self.cs_points.View == slice) & (self.cs_points.Surface == surface)].Index).to_numpy(), :]
        return np.linalg.norm(vertices[1:, ] - vertices[:-1, ], axis=1).sum().item()



