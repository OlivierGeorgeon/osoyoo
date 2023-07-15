from pyrr import Quaternion
from ..Memory.EgocentricMemory.Experience import EXPERIENCE_LOCAL_ECHO, EXPERIENCE_CENTRAL_ECHO, \
    EXPERIENCE_ALIGNED_ECHO
from autocat.Memory.PhenomenonMemory.Affordance import Affordance

PHENOMENON_DELTA = 300


class Integrator:
    """The integrator creates and updates the phenomena from the experiences"""
    def __init__(self, workspace):
        """Constructor"""
        self.workspace = workspace
        # self.phenomena = []

    def integrate(self):
        """Create phenomena and update cells in allocentric memory"""

        # The new experiences generated during this round
        new_experiences = [e for e in self.workspace.memory.egocentric_memory.experiences.values()
                           if (e.clock >= self.workspace.clock)]

        # The new affordances
        new_affordances = []
        for e in new_experiences:
            if e.type != EXPERIENCE_LOCAL_ECHO:
                # The position of the affordance in allocentric memory
                affordance_point = self.workspace.memory.egocentric_to_allocentric(e.point)
                new_affordances.append(Affordance(affordance_point, e))
                # print("Experience:", e.type, ", point:", affordance_point)

        # Mark the area covered by the echo in allocentric memory
        for a in [a for a in new_affordances if a.experience.type
                  in [EXPERIENCE_CENTRAL_ECHO, EXPERIENCE_ALIGNED_ECHO]]:
            self.workspace.memory.allocentric_memory.mark_echo_area(a)

        # Try to attach the new affordances to existing phenomena and remove these affordances
        new_affordances, position_correction = self.workspace.memory.phenomenon_memory.update_phenomena(new_affordances)

        # Adjust the robot's position in allocentric memory
        # print("Position correction due to phenomenon update", position_correction)
        self.workspace.memory.allocentric_memory.move(Quaternion([0, 0, 0, 1]), position_correction, self.workspace.clock)

        # Create new hypothetical phenomena from remaining affordances
        self.workspace.memory.phenomenon_memory.create_phenomena(new_affordances)

        # Stores the remaining new affordances in allocentric memory
        # self.allocentric_memory.affordances.extend(new_affordances) Not sure why

        return None
