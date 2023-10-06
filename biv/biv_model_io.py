from pathlib import Path
import numpy as np
from mesh_tools import Mesh
import inspect

# get the default model folder
DEFAULT_MODEL_FOLDER = Path(inspect.getabsfile(inspect.currentframe())).parent / "model"


def load_biv_model(model_folder: Path = DEFAULT_MODEL_FOLDER):
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


def load_fitted_model(fitted_file: Path, model_folder: Path = DEFAULT_MODEL_FOLDER, name: str = 'Mesh'):
    """
    Read a fitted model.

    :param fitted_file: a fitted model as a text file
    :param model_folder: see load_biv_model function
    :param name: identify the model name
    :return: a dictionary with the following filed:
        'control_points': the control points of the model
        'mesh': a Mesh model that defines the biventricular model (see mesh_tools.mesh.Mesh class)
    """
    # read the model
    biv_model = load_biv_model(model_folder)

    # read the control points
    control_points = np.loadtxt(fitted_file, delimiter=',',skiprows=1, usecols=[0,1,2]).astype(float)

    # calculate the mesh points
    vertices = np.dot(biv_model['subdiv'], control_points)

    # create the model
    model = Mesh(name)
    model.set_nodes(vertices * 10)
    model.set_elements(biv_model['faces'])
    model.set_materials(biv_model['materials'][:, 0], biv_model['materials'][:, 1])

    return {
        'control_points': control_points,
        'mesh': model
    }

