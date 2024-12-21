# A list of python functions that I commonly use (or not)
import numpy as np

def avg_radius(
    geom: np.array
) -> float:
    """
    Compute the 'average radius' of a geometry as the average distance of each atom to the center of mass

    :param geom: array containing system coordinates
    :returns: average radius as a float
    """
    assert geom.ndim == 2, "geom dimension must be 2"
    assert len(geom) > 0 and len(geom[0]) == 3, "geometry input must have 3 (x, y, z) coordinates for at least one atom"

    num_atoms = len(geom)
    x_cm, y_cm, z_cm = 0, 0, 0
    for atom in geom:
        x_cm += atom[0] / num_atoms
        y_cm += atom[1] / num_atoms
        z_cm += atom[2] / num_atoms

    return np.sqrt(np.sum(np.square(geom - [x_cm, y_cm, z_cm]) / num_atoms))

