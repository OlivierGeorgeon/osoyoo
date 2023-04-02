import numpy as np
from pyrr import matrix44
from .Phenomenon import Phenomenon
from ..Memory.EgocentricMemory.Experience import EXPERIENCE_PLACE, EXPERIENCE_FLOOR

TERRAIN_EXPERIENCE_TYPES = [EXPERIENCE_PLACE, EXPERIENCE_FLOOR]


class PhenomenonTerrain(Phenomenon):
    """A hypothetical phenomenon related to floor detection"""
    def __init__(self, affordance):
        super().__init__(affordance)
        # print("New phenomenon terrain with experience clock:", affordance.experience.clock)

    def update(self, affordance):
        """Test if the affordance is within the acceptable delta from the position of the phenomenon,
        if yes, add the affordance to the phenomenon, and return the robot's position correction."""
        # All terrain affordances are always added
        if affordance.experience.type in TERRAIN_EXPERIENCE_TYPES:
            affordance.point = np.array(affordance.point - self.point, dtype=int)
            # TODO Perhaps clone the affordance
            position_correction = np.array([0, 0, 0], dtype=int)
            self.affordances.append(affordance)
            return position_correction
        # No position correction
        return None  # Must return None to check if this affordance can be associated with another phenomenon

    def save(self, experiences):
        """Return a clone of the phenomenon for memory snapshot"""
        # Use the experiences cloned when saving egocentric memory
        saved_phenomenon = PhenomenonTerrain(self.origin_affordance)
        super().save(saved_phenomenon, experiences)
        return saved_phenomenon

