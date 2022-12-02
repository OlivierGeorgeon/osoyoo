from ..EgocentricMemory.Experience import EXPERIENCE_PLACE
# from ...Integrator.Phenomenon import Phenomenon

CELL_PHENOMENON = 'phenomenon'
CELL_UNKNOWN = 'Unknown'


class GridCell:
    """This class represents a cell in a hexagrid
    """
    def __init__(self, i, j):
        """Constructor of the class, i and j are the coordinates of the cell in the grid
        """
        self.i = i
        self.j = j
        self.status = CELL_UNKNOWN
        # self.occupied = False  # True if the cell is occupied by the agent
        self.experiences = list()  # Used in Synthesizer to store the experiences that happened on the cell
        self.confidence = 1
        self.phenomenon = None

    def __str__(self):
        return "(" + str(self.i)+','+str(self.j) + ")"

    # def occupy(self):
    #     self.occupied = True
    #
    # def leave(self):
    #     self.occupied = False

    # Commented by OG 23/09/2022
    # def add_interaction(self, experience):
    #     """Add a new interaction to the list of interactions
    #     """
    #     self.experiences.append(experience)
    #     if experience not in self.experiences:
    #         self.experiences.append(experience)

    def set_to(self, status):
        """Change the cell status, print an error if the status is invalid."""
        assert(status in ["Blocked", CELL_UNKNOWN, "Line", "Something", EXPERIENCE_PLACE, CELL_PHENOMENON])
        self.status = status

    # def allocate_phenomenon(self, phenomenon):
    #     """Allocate a phenomenon to this cell"""
    #     self.phenomenon = phenomenon
    #     self.set_to(CELL_PHENOMENON)
