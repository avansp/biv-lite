import numpy as np

def flip_elements(mesh, material_id: int):
    mesh.elements[mesh.materials == material_id, :] = (
        np.array([mesh.elements[mesh.materials == material_id, 0],
                  mesh.elements[mesh.materials == material_id, 2],
                  mesh.elements[mesh.materials == material_id, 1]]).T)

    return mesh

