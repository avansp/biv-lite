from meshing.mesh import Mesh
import numpy as np
import inspect
from pathlib import Path
from typing import Dict


def load_biv_model(model_folder) -> Dict:
    """
    Load a biventricular model

    Notes:
    This function needs a model_folder where it contains the following files:
    * subdivision_matrix.txt
    * ETIndicesSorted.txt
    * ETIndicesMaterials.txt
    * epi_to_septum_ETindices.txt

    :param model_folder: A subdivision model folder (see notes above).
    :return: a dictionary that contains the subdivision matrix, faces, and materials for 3D mesh structure
    """
    # check the model folder
    subdivision_matrix_file = model_folder / 'subdivision_matrix.txt'
    assert subdivision_matrix_file.is_file(), f"Cannot find subdivision_matrix.txt in folder: {model_folder}"

    elements_file = model_folder / 'ETIndicesSorted.txt'
    assert elements_file.is_file(), f"Cannot find ETIndicesSorted.txt in folder: {model_folder}"

    material_file = model_folder / 'ETIndicesMaterials.txt'
    assert material_file.is_file(), f"Cannot find ETIndicesMaterials.txt in folder: {model_folder}"

    mat = np.loadtxt(material_file, dtype='str')
    # convert labels to integer corresponding to the sorted list
    # of unique labels types
    unique_material = np.unique(mat[:, 1])
    materials = np.zeros(mat.shape)
    for index, m in enumerate(unique_material):
        face_index = mat[:, 1] == m
        materials[face_index, 0] = mat[face_index, 0].astype(int)
        materials[face_index, 1] = [index] * np.sum(face_index)

    # read and return the model
    return {
        'subdiv': (np.loadtxt(subdivision_matrix_file)).astype(float),
        'faces': np.loadtxt(elements_file).astype(int) - 1,
        'materials': materials.astype(int)
    }


class BivMesh(Mesh):
    """
    Wrap Mesh class to make it easier to work with as a biventricular model.
    """
    DEFAULT_MODEL_FOLDER = Path(inspect.getabsfile(inspect.currentframe())).parent / "model"

    def __init__(self,  control_points, name: str = "biv_mesh", model_folder: Path = DEFAULT_MODEL_FOLDER):
        super().__init__(name)

        self.control_points = control_points

        # select only necessary variables from the Biventricular template model
        biv_model = load_biv_model(model_folder)
        self.subdiv_matrix = biv_model['subdiv']

        # create the model
        self.set_nodes(np.dot(self.subdiv_matrix, self.control_points))
        self.set_elements(biv_model['faces'])
        self.set_materials(biv_model['materials'][:, 0], biv_model['materials'][:, 1])

    @classmethod
    def from_fitted_model(cls, model_file: str | Path, **kwargs):
        """Load fitted model and returns BivMesh object."""
        # read the control points
        control_points = np.loadtxt(model_file, delimiter=',',skiprows=1, usecols=[0,1,2]).astype(float)

        return BivMesh(control_points, **kwargs)

