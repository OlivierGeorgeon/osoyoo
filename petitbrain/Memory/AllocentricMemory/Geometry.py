########################################################################################
# The math used to handle the hexagonal grid
# https://www.redblobgames.com/grids/hexagons/
# Orientation: flat_top.
# Coordinate system: Axial
# Pooling with aperture of 7
# https://ieeexplore.ieee.org/document/8853238
########################################################################################

import numpy as np
from petitbrain.Memory import CELL_RADIUS, GRID_WIDTH, GRID_HEIGHT


def cell_to_point(q, r, radius=CELL_RADIUS):
    """Convert cell axial coordinates to allocentric position"""
    x = (3/2 * q) * radius
    y = (np.sqrt(3)/2 * q + np.sqrt(3) * r) * radius
    return np.transpose(np.array([x, y]), axes=(1, 2, 0))


def point_to_cell(point, radius=CELL_RADIUS):
    """Convert allocentric position to cell axial coordinates."""
    q = (2 * point[0]) / (3 * radius)
    r = (-point[0] + np.sqrt(3) * point[1]) / (3 * radius)
    q, r = axial_round(q, r)
    # Rhombus wrap
    q = (q + int((GRID_WIDTH - 0.5) // 2)) % GRID_WIDTH - int((GRID_WIDTH - 0.5) // 2)
    r = (r + int((GRID_HEIGHT - 0.5) // 2)) % GRID_HEIGHT - int((GRID_HEIGHT - 0.5) // 2)
    return q, r


def axial_round(q, r):
    """Round the axial coordinates"""
    x = round(q)
    z = round(r)
    y = round(-x - z)

    x_diff = abs(x - q)
    y_diff = abs(y - (-x - z))
    z_diff = abs(z - r)

    if x_diff > y_diff and x_diff > z_diff:
        x = -y - z
    elif y_diff > z_diff:
        y = -x - z
    else:
        z = -x - y
    return x, z


def is_pool(i, j):
    """Return 1 if this cell is a pool center with aperture 7"""
    # https://ieeexplore.ieee.org/document/8853238
    return np.where((i - 2 * j) % 7 == 0, 1, 0)


def is_inside_rectangle(x, y, r):
    """Return True for the points that are inside the rectangle"""
    # https://stackoverflow.com/questions/2752725/finding-whether-a-point-lies-inside-a-rectangle-or-not
    d1 = (r[1, 0] - r[0, 0]) * (y - r[0, 1]) - (x - r[0, 0]) * (r[1, 1] - r[0, 1]) > 0
    d2 = (r[2, 0] - r[1, 0]) * (y - r[1, 1]) - (x - r[1, 0]) * (r[2, 1] - r[1, 1]) > 0
    d3 = (r[3, 0] - r[2, 0]) * (y - r[2, 1]) - (x - r[2, 0]) * (r[3, 1] - r[2, 1]) > 0
    d4 = (r[0, 0] - r[3, 0]) * (y - r[3, 1]) - (x - r[3, 0]) * (r[0, 1] - r[3, 1]) > 0
    return np.logical_and(np.logical_and(np.logical_and(d1, d2), d3), d4)
