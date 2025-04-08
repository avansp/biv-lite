import numpy as np
from scipy.interpolate import make_splrep

def flip_elements(mesh, material_id: int):
    mesh.elements[mesh.materials == material_id, :] = (
        np.array([mesh.elements[mesh.materials == material_id, 0],
                  mesh.elements[mesh.materials == material_id, 2],
                  mesh.elements[mesh.materials == material_id, 1]]).T)

    return mesh

def perinterp(x: np.array, y: np.array, k: int = 1):
    """Periodic 1D interpolation.

    :param x: x samples as 1D array
    :param y: y samples as 1D array
    :param k: number of samples to be replicated beginning & end

    :return: a function
    """

    # append the first k-sample to the end and last k-sample to the beginning
    xs = np.concat((x[-k:] - 1.0, x, 1.0 + x[:k]))
    ys = np.concat((y[-k:], y, y[:k]))

    # return the interpolation function
    return make_splrep(xs, ys)



