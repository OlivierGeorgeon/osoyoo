import matplotlib.path as mpath
from .Hexagonal_geometry import cell_to_point

CELL_UNKNOWN = 'Unknown'
CELL_NO_ECHO = 'no_echo'


class GridCell:
    """This class represents an hexagonal cell in allocentric memory"""
    def __init__(self, i, j, cell_radius):
        """Constructor of the class, i and j are the coordinates of the cell in the grid"""
        self.i = i
        self.j = j
        self.radius = cell_radius  # The radius of the outer circle

        self._point = cell_to_point(i, j)  # Must not be changed

        self.status = [CELL_UNKNOWN,  # Place
                       CELL_UNKNOWN,  # Interaction
                       CELL_UNKNOWN,  # No echo
                       CELL_UNKNOWN,  # Focus
                       CELL_UNKNOWN]  # Prompt
        self.color_index = 0
        self.clock_place = 0
        self.clock_interaction = 0
        self.clock_phenomenon = 0
        self.clock_no_echo = 0
        self.clock_focus = 0
        self.clock_prompt = 0
        self.phenomenon_id = None

    def __str__(self):
        """String representation of the cell for console display"""
        return "(%+d,%+d)" % (self.i, self.j)

    def label(self):
        """Label of the cell for display on click in allocentricView"""
        label = repr(self.status) + " Clocks: ["
        label += str(self.clock_place) + ", "
        label += str(self.clock_interaction) + ", "
        label += str(self.clock_no_echo) + ", "
        label += str(self.clock_focus) + ", "
        label += str(self.clock_prompt) + "]"
        if self.phenomenon_id is not None:
            label += " Phenomenon:" + str(self.phenomenon_id)
        return label

    def point(self):
        """Return a clone of the cell's point"""
        return self._point.copy()

    def is_known(self):
        """Return True if something is known in this cell"""
        return self.status != [CELL_UNKNOWN, CELL_UNKNOWN, CELL_UNKNOWN, CELL_UNKNOWN, CELL_UNKNOWN]
        # return self.status[0] != CELL_UNKNOWN or self.status[1] != CELL_UNKNOWN or self.status[2] != CELL_UNKNOWN \
        #     or self.status[3] != CELL_UNKNOWN or self.clock_prompt > 0

    def is_inside(self, path):
        """True if this cell is inside the path"""
        # path = mpath.Path(polygon)
        # return delaunay.find_simplex(self._point[0:2]) >= 0  This is slower
        return path.contains_point(self._point[0:2])

    def interest_value(self, clock):
        """Return how much this cell is interesting to visit"""
        interest_value = 0
        # Interesting if not visited
        if self.status[0] == CELL_UNKNOWN:
            interest_value = 1
        # Not interesting if already prompted
        if self.clock_prompt > 0:
            interest_value = -10
        # Very interesting if colored
        # Not working because stop on the cell and don't change the clock_place
        # if self.color_index is not None and self.color_index > 0 and clock - self.clock_place > 5:
        #     interest_value = 10
        return interest_value

    def is_pool(self):
        """True if this cell is used for pooling with aperture 7"""
        # https://ieeexplore.ieee.org/document/8853238
        # even: i = 3n + m, j = -2n + 4m
        # odd: i = 3n + m -2, j = -2n + 4m + 1
        pool_even = (-4 * self.i + self.j) % 14 == 0
        pool_odd = (-4 * self.i + self.j - 9) % 14 == 0
        return pool_even or pool_odd

    def save(self):
        """Return a clone of the cell to save a snapshot of allocentric memory"""
        saved_cell = GridCell(self.i, self.j, self.radius)
        # Clone the content
        saved_cell.status = self.status.copy()
        saved_cell.color_index = self.color_index
        saved_cell.clock_place = self.clock_place
        saved_cell.clock_interaction = self.clock_interaction
        saved_cell.clock_phenomenon = self.clock_phenomenon
        saved_cell.clock_no_echo = self.clock_no_echo
        saved_cell.clock_focus = self.clock_focus
        saved_cell.clock_prompt = self.clock_prompt
        saved_cell.phenomenon_id = self.phenomenon_id
        return saved_cell
