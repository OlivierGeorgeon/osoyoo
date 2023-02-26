import math
import numpy as np
import matplotlib.path as mpath

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
        self.point = np.array([x, y, 0], dtype=int)

        self.status = [CELL_UNKNOWN,  # Place
                       CELL_UNKNOWN,  # Interaction
                       CELL_UNKNOWN,  # No echo
                       CELL_UNKNOWN]  # Focus
        self.clocks = [0, 0, 0, 0]  # The latest clocks attached with each layer
        self.experiences = list()  # Used in Synthesizer to store the experiences that happened on the cell
        self.phenomenon = None

    def __str__(self):
        """String representation of the cell for console display"""
        return "(%+d,%+d)" % (self.i, self.j)

    def is_known(self):
        """Return True if something is known in this cell"""
        return self.status[0] != CELL_UNKNOWN or self.status[1] != CELL_UNKNOWN or self.status[2] != CELL_UNKNOWN \
            or self.status[3] != CELL_UNKNOWN

    def is_inside(self, polygon):
        """True if this cell is inside the polygon"""
        path = mpath.Path(polygon)
        return path.contains_point(self.point[0:2])

    def save(self, experiences):
        """Return a clone of the cell to save a snapshot of allocentric memory"""
        # Use the experiences cloned when saving egocentric memory
        saved_cell = GridCell(self.i, self.j, self.radius)
        # Clone the content
        saved_cell.status = self.status.copy()
        saved_cell.clocks = self.clocks.copy()
        saved_cell.experiences = [experiences[e.id] for e in self.experiences]
        if self.phenomenon is not None:
            saved_cell.phenomenon = self.phenomenon.save(experiences)
        return saved_cell
