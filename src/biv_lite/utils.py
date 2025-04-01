import numpy as np

def flip_elements(mesh, material_id: int):
    mesh.elements[mesh.materials == material_id, :] = (
        np.array([mesh.elements[mesh.materials == material_id, 0],
                  mesh.elements[mesh.materials == material_id, 2],
                  mesh.elements[mesh.materials == material_id, 1]]).T)

    return mesh

# using pyvista format, you have to add number of points for each element
def to_pyvista_faces(elements: np.ndarray) -> np.ndarray:
    return np.hstack([np.ones((elements.shape[0], 1)) * 3, elements]).astype(np.int32)

