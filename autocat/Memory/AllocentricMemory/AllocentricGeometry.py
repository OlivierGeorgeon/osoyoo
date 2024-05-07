import numpy as np


def is_inside_rectangle(x, y, r):
    """Return True for the points that are inside the rectangle"""
    # https://stackoverflow.com/questions/2752725/finding-whether-a-point-lies-inside-a-rectangle-or-not
    d1 = (r[1, 0] - r[0, 0]) * (y - r[0, 1]) - (x - r[0, 0]) * (r[1, 1] - r[0, 1]) > 0
    d2 = (r[2, 0] - r[1, 0]) * (y - r[1, 1]) - (x - r[1, 0]) * (r[2, 1] - r[1, 1]) > 0
    d3 = (r[3, 0] - r[2, 0]) * (y - r[2, 1]) - (x - r[2, 0]) * (r[3, 1] - r[2, 1]) > 0
    d4 = (r[0, 0] - r[3, 0]) * (y - r[3, 1]) - (x - r[3, 0]) * (r[0, 1] - r[3, 1]) > 0
    return np.logical_and(np.logical_and(np.logical_and(d1, d2), d3), d4)


def is_inside_polygon(p, r):
    """Return True if the point is inside the polygon"""
    # https://stackoverflow.com/questions/2752725/finding-whether-a-point-lies-inside-a-rectangle-or-not
    d1 = (r[1, 0] - r[0, 0]) * (p[1] - r[0, 1]) - (p[0] - r[0, 0]) * (r[1, 1] - r[0, 1]) > 0
    d2 = (r[2, 0] - r[1, 0]) * (p[1] - r[1, 1]) - (p[0] - r[1, 0]) * (r[2, 1] - r[1, 1]) > 0
    d3 = (r[3, 0] - r[2, 0]) * (p[1] - r[2, 1]) - (p[0] - r[2, 0]) * (r[3, 1] - r[2, 1]) > 0
    d4 = (r[0, 0] - r[3, 0]) * (p[1] - r[3, 1]) - (p[0] - r[3, 0]) * (r[0, 1] - r[3, 1]) > 0
    return np.logical_and(np.logical_and(np.logical_and(d1, d2), d3), d4)
