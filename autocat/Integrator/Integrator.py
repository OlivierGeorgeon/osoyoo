import numpy
from ..Memory.EgocentricMemory.Experience import EXPERIENCE_LOCAL_ECHO
from .Affordance import Affordance
from .Phenomenon import Phenomenon

PHENOMENON_DELTA = 300


class Integrator:
    """The integrator creates and updates the phenomena from the experiences"""
    def __init__(self, workspace):
        """Constructor"""
        self.workspace = workspace
        self.egocentric_memory = workspace.memory.egocentric_memory
        self.allocentric_memory = workspace.memory.allocentric_memory
        self.body_memory = workspace.memory.body_memory
        self.phenomena = []
        # self.last_projection_for_context = []
        self.last_used_id = 0

    def integrate(self):
        """Create phenomena and update cells in allocentric memory"""

        # The new experiences generated during this round
        new_experiences = [e for e in self.egocentric_memory.experiences if (e.id > self.last_used_id)]
        self.last_used_id = max([e.id for e in new_experiences], default=self.last_used_id)

        # The new affordances
        new_affordances = []
        for e in new_experiences:
            if e.type != EXPERIENCE_LOCAL_ECHO:
                affordance_point = e.allocentric_from_matrices(self.workspace.memory.body_memory.body_direction_matrix(),
                                                               self.allocentric_memory.body_position_matrix())
                new_affordances.append(Affordance(affordance_point, e))

        # Keep only echo affordances (for now)
        # affordances_echo = [a for a in new_affordances if (a.experience.type == EXPERIENCE_CENTRAL_ECHO or
        #                                                    a.experience.type == EXPERIENCE_ALIGNED_ECHO)]

        # Try to attach the new affordances to existing phenomena and remove these affordances
        new_affordances, position_correction = self.update_phenomena(new_affordances)

        # Adjust the robot's position in allocentric memory
        self.allocentric_memory.move(0, position_correction, is_egocentric_translation=False)

        # Create new hypothetical phenomena from remaining affordances
        # self.create_phenomena(new_affordances)

        # Stores the remaining new affordances in allocentric memory
        self.allocentric_memory.affordances.extend(new_affordances)

        # Mark the new experiences in allocentric memory by changing the cell status
        # self.apply_status_experience_to_cells([e for e in new_experiences if e.type != EXPERIENCE_LOCAL_ECHO])

        # Display the validated phenomena in the grid
        # self.allocentric_memory.attach_phenomena_to_cells()

        return None

    def update_phenomena(self, affordances):
        """Try to attach a list of affordances to phenomena in the list .
        Returns the affordances that have not been attached, and the average translation"""
        position_correction = numpy.array([0, 0, 0], dtype=numpy.int16)
        sum_translation = numpy.array([0, 0, 0], dtype=numpy.int16)
        number_of_add = 0
        remaining_affordances = affordances.copy()

        for affordance in affordances:
            for phenomenon in self.phenomena:
                delta = phenomenon.update(affordance)
                if delta is not None:
                    sum_translation += delta
                    number_of_add += 1
                    remaining_affordances.remove(affordance)
                    break
        if number_of_add > 0:
            position_correction = numpy.divide(sum_translation, number_of_add)

        return remaining_affordances, position_correction

    def create_phenomena(self, affordances):
        """Create new phenomena from the list of experiences"""
        new_phenomena = []
        for affordance in affordances:
            if len(new_phenomena) == 0:
                new_phenomena.append(Phenomenon(affordance))
            else:
                clustered = False
                # Look if the new affordance can be attached to an existing new phenomenon
                for new_phenomenon in new_phenomena:
                    if new_phenomenon.update(affordance) is not None:
                        clustered = True
                        break
                if not clustered:
                    new_phenomena.append(Phenomenon(affordance))

        self.phenomena.extend(new_phenomena)
