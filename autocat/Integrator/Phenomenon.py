import math
from pyrr import matrix44
from .Affordance import Affordance


class Phenomenon:
    """An hypothetical phenomenon"""
    def __init__(self, echo_experience, position_matrix, acceptable_delta=300):
        """Constructor
        Parameters:
            echo_experience: the first echo interaction of the object phenomenon
            position_matrix: the matrix to place the phenomenon in allocentric memory
            acceptable_delta: the acceptable delta between the allocentric coordinates of a new echo interaction
            and the center of the object phenomenon"""
        self.experiences = [echo_experience]
        self.position_matrix = position_matrix

        # Record the first affordance of the phenomenon
        self.affordances = [Affordance(0, 0, echo_experience)]

        self.acceptable_delta = acceptable_delta

        # The coordinates of this phenomenon in allocentric memory
        x, y, _ = matrix44.apply_to_vector(self.position_matrix, [0, 0, 0])
        self.allo_coordinates = [(x, y)]
        self.center = [x, y]

        self.has_been_validated = False
        self.printed = False

    def add_affordance(self, x, y, experience):
        """Add an affordance made from this experience at this position"""
        self.experiences.append(experience)
        self.allo_coordinates.append((x, y))
        self.affordances.append(Affordance(x, y, experience))

        if not self.has_been_validated:
            self.compute_center()

    def compute_center(self):
        """Compute the center of the object phenomenon"""
        sum_x = 0
        sum_y = 0
        i = 0
        # self.center = np.mean(self.allo_coordinates,axis=0)
        for allo_coord in self.allo_coordinates:
            sum_x += allo_coord[0]
            sum_y += allo_coord[1]
            i += 1
        self.center = (int(sum_x/i), int(sum_y/i))
        # self.cell_i, self.cell_j = self.hexa_memory.convert_pos_in_cell(self.center[0], self.center[1])

    def try_and_add(self, experience, position_matrix):
        """Test if the echo interaction is in the acceptable delta of the center of the phenomenon,
        if yes, add it to the phenomenon"""
        x, y, _ = matrix44.apply_to_vector(position_matrix, [0, 0, 0])
        allocentric_coordinates = [x, y]
        if math.dist(allocentric_coordinates, self.center) < self.acceptable_delta:
            dist_x = self.center[0]-allocentric_coordinates[0]
            dist_y = self.center[1]-allocentric_coordinates[1]
            self.add_affordance(experience, position_matrix)
            return True, (dist_x, dist_y)
        else:
            return False, None

    def try_to_validate(self, number_of_echos_needed):
        """Try to validate the phenomenon, i.e. consider this phenomenon as valid.
        To do so, the number of echo interactions needed to be added must be reached"""
        if len(self.experiences) >= number_of_echos_needed:
            self.has_been_validated = True
        return self.has_been_validated
