import numpy as np
from pyrr import matrix44
from webcolors import name_to_rgb
from .Phenomenon import Phenomenon
from ..Memory.EgocentricMemory.Experience import EXPERIENCE_PLACE, EXPERIENCE_FLOOR, COLOR_FLOOR

TERRAIN_EXPERIENCE_TYPES = [EXPERIENCE_PLACE, EXPERIENCE_FLOOR]


class PhenomenonTerrain(Phenomenon):
    """A hypothetical phenomenon related to floor detection"""
    def __init__(self, affordance):
        super().__init__(affordance)
        # print("New phenomenon terrain with experience clock:", affordance.experience.clock)

    def update(self, affordance):
        """Test if the affordance is within the acceptable delta from the position of the phenomenon,
        if yes, add the affordance to the phenomenon, and return the robot's position correction."""

        # If the origin affordance is not a color floor and this affordance is then this affordance becomes the origin affordance
        if affordance.experience.type == EXPERIENCE_FLOOR and affordance.experience.color == name_to_rgb(COLOR_FLOOR):
            if self.origin_affordance.experience.type != EXPERIENCE_FLOOR or affordance.experience.color != name_to_rgb(COLOR_FLOOR):
                self.origin_affordance = affordance
                # TODO perhaps move the phenomenon point of reference

        # All terrain affordances are always added
        if affordance.experience.type in TERRAIN_EXPERIENCE_TYPES:
            affordance.point = np.array(affordance.point - self.point, dtype=int)
            # TODO Perhaps clone the affordance
            position_correction = np.array([0, 0, 0], dtype=int)
            self.affordances.append(affordance)
            if affordance.is_similar_to(self.origin_affordance):
                # Correct the robot's position
                # position_correction = self.origin_affordance.point - affordance.point
                print("Near origin affordance")
            return position_correction
        # No position correction
        return None  # Must return None to check if this affordance can be associated with another phenomenon

    def save(self, experiences):
        """Return a clone of the phenomenon for memory snapshot"""
        # Use the experiences cloned when saving egocentric memory
        saved_phenomenon = PhenomenonTerrain(self.origin_affordance)
        super().save(saved_phenomenon, experiences)
        return saved_phenomenon

