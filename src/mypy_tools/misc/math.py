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

def convert_time(
    time_str: str,
    unit: str,
) -> float:
    from datetime import datetime

    days = 0
    if '-' in time_str:
        days = time_str.split('-')[0]
        time_str = time_str.split('-')[1]

    time = datetime.strptime(time_str, '%H:%M:%S')
    total_time = int(days) * 86400 + time.hour * 3600 + time.minute * 60 + time.second

    if unit == 'h':
        return total_time / 3600
    elif unit == 'm':
        return total_time / 60
    elif unit == 's':
        return total_time
    else:
        raise Exception("Improper time unit passed in time conversion")

def convert_memory(
    mem_str: str,
    unit: str,
) -> float:
    scale= {'B': 0, 'K': 1, 'M': 2, 'G': 3, 'T': 4}

    unit_diff = scale[mem_str[-1]] - scale[unit]
    return float(mem_str[:-1]) * (1024 ** unit_diff)
