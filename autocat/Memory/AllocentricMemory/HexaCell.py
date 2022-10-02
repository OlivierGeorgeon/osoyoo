from ..EgocentricMemory.Experience import EXPERIENCE_PLACE


class HexaCell:
    """This class represents a cell in a hexagrid
    """
    def __init__(self, x, y):
        """Constructor of the class, x and y are the coordinates of the cell
        """
        self.x = x
        self.y = y
        self.status = "Unknown"
        self.occupied = False  # True if the cell is occupied by the agent
        self.experiences = list()  # Used in Synthesizer to store the experiences that happened on the cell
        self.confidence = 1

    def __str__(self):
        return "(" + str(self.x)+','+str(self.y) + ")"

    def occupy(self):
        self.occupied = True

    def leave(self):
        self.occupied = False

    # Commented by OG 23/09/2022
    # def add_interaction(self, experience):
    #     """Add a new interaction to the list of interactions
    #     """
    #     self.experiences.append(experience)
    #     if experience not in self.experiences:
    #         self.experiences.append(experience)

    def set_to(self, status):
        """Change the cell status, print an error if the status is invalid.
        """
        assert(status == "Blocked" or status == "Unknown" or status == "Line" or
               status == "Something" or status == EXPERIENCE_PLACE)
        self.status = status
        # print("Unknown status : \" ", status, ", existing status : \"Free\" (when has been visited), \"Occupied\" (when robot is on it), \"Blocked\" (when object is on it), \"Unknown\" (when has not been visited)")