import math
import numpy as np
import matplotlib.path as mpath
from ..EgocentricMemory.Experience import EXPERIENCE_PLACE

CELL_PHENOMENON = 'phenomenon'
CELL_UNKNOWN = 'Unknown'
CELL_NO_ECHO = 'no_echo'


class GridCell:
    """This class represents an hexagonal cell in allocentric memory"""
    def __init__(self, i, j, cell_radius):
        """Constructor of the class, i and j are the coordinates of the cell in the grid"""
        self.i = i
        self.j = j
        self.radius = cell_radius

        # Compute the position of this cell
        cell_height = math.sqrt((2 * cell_radius) ** 2 - cell_radius ** 2)
        if j % 2 == 0:
            x = i * 3 * cell_radius
            y = cell_height * (j / 2)
        else:
            x = (1.5 * cell_radius) + i * 3 * cell_radius
            y = (cell_height / 2) + (j - 1) / 2 * cell_height
        self.point = np.array([x, y, 0])

        # self.point = np.array([0, 0, 0])  # Is initialized just after the creation of the cell

        self.status = [CELL_UNKNOWN, CELL_UNKNOWN, CELL_UNKNOWN, CELL_UNKNOWN]
        self.experiences = list()  # Used in Synthesizer to store the experiences that happened on the cell
        self.phenomenon = None

    def __str__(self):
        # return "(" + "%+d" % self.i + ',' + "%+d" % self.j + ")"
        return "(%+d,%+d)" % (self.i, self.j)

    # def set_to(self, status):
    #     """Change the cell status, print an error if the status is invalid."""
    #     assert(status in ["Blocked", CELL_UNKNOWN, "Line", "Something", EXPERIENCE_PLACE, CELL_PHENOMENON])
    #     self.status[1] = status

    def is_inside(self, polygon):
        """True if this cell is inside the polygon"""
        path = mpath.Path(polygon)
        return path.contains_point(self.point[0:2])
