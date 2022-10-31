import math
from pyrr import matrix44
from .Affordance import Affordance

PHENOMENON_DELTA = 300  # (mm) distance between experiences to be considered the same phenomenon


class Phenomenon:
    """An hypothetical phenomenon"""
    def __init__(self, echo_experience, position_matrix):
        """Constructor
        Parameters:
            echo_experience: the first echo interaction of the object phenomenon
            position_matrix: the matrix to place the phenomenon in allocentric memory
            acceptable_delta: the acceptable delta between the allocentric coordinates of a new echo interaction
            and the center of the object phenomenon"""
        # self.experiences = [echo_experience]
        self.position_matrix = position_matrix

        # Record the first affordance of the phenomenon
        self.affordances = [Affordance(0, 0, echo_experience)]

        # The coordinates of this phenomenon in allocentric memory
        self.x, self.y, _ = matrix44.apply_to_vector(self.position_matrix, [0, 0, 0])
        # self.allo_coordinates = [(x, y)]
        # self.center = [x, y]

        self.has_been_validated = False
        self.printed = False

    def add_affordance(self, x, y, experience):
        """Add an affordance made from this experience at this position"""
        self.affordances.append(Affordance(x, y, experience))

        # TODO: Adjust the center of the phenomenon when we can move it in phenomenon view
        # self.compute_center()

    def compute_center(self):
        """Adjust the center of the phenomenon and the relative position of affordances"""
        sum_x = 0.
        sum_y = 0.
        i = 0.
        # self.center = np.mean(self.allo_coordinates,axis=0)
        for affordance in self.affordances:
            sum_x += affordance.position_matrix[3, 0]
            sum_y += affordance.position_matrix[3, 1]
            i += 1
        # Move the phenomenon's position to the center of the affordances
        self.position_matrix[3, 0] += int(sum_x/i)
        self.position_matrix[3, 1] += int(sum_y/i)
        # Adjust the affordances' position
        for affordance in self.affordances:
            affordance.position_matrix[3, 0] -= int(sum_x/i)
            affordance.position_matrix[3, 1] -= int(sum_y/i)

    def try_and_add(self, experience, position_matrix, trust_mode):
        """Test if the echo interaction is in the acceptable delta of the center of the phenomenon,
        if yes, add it to the phenomenon"""
        x, y, _ = matrix44.apply_to_vector(position_matrix, [0, 0, 0])
        if math.dist([x, y], [self.x, self.y]) < PHENOMENON_DELTA:
            dist_x, dist_y = x - self.x, y - self.y
            if trust_mode:
                self.add_affordance(0, 0, experience)
            else:
                self.add_affordance(dist_x, dist_y, experience)
            return True, (-dist_x, -dist_y)
        else:
            return False, None

    def try_to_validate(self, number_of_echos_needed):
        """Try to validate the phenomenon, i.e. consider this phenomenon as valid.
        To do so, the number of echo interactions needed to be added must be reached"""
        if len(self.affordances) >= number_of_echos_needed:
            self.has_been_validated = True
        return self.has_been_validated
