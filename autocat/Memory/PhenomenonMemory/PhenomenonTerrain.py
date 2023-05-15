import numpy as np
from pyrr import matrix44
from .Phenomenon import Phenomenon
from autocat.Memory.EgocentricMemory.Experience import EXPERIENCE_PLACE, EXPERIENCE_FLOOR


TERRAIN_EXPERIENCE_TYPES = [EXPERIENCE_PLACE, EXPERIENCE_FLOOR]


class PhenomenonTerrain(Phenomenon):
    """A hypothetical phenomenon related to floor detection"""
    def __init__(self, affordance):
        super().__init__(affordance)
        # print("New phenomenon terrain with experience clock:", affordance.experience.clock)
        self.confidence = 0.1  # Must not be null to allow position correction

    def update(self, affordance):
        """Test if the affordance is within the acceptable delta from the position of the phenomenon,
        if yes, add the affordance to the phenomenon, and return the robot's position correction."""

        # If this affordance is a color floor and the the previous origin was not then make this affordance the origin
        if affordance.experience.type == EXPERIENCE_FLOOR and affordance.experience.color_index > 0:
            if self.origin_affordance.experience.type != EXPERIENCE_FLOOR or self.origin_affordance.experience.color_index == 0:
                self.origin_affordance = affordance
                for a in self.affordances:
                    a.point -= affordance.point.astype(int) - self.point.astype(int)
                self.point = affordance.point.copy()
                # The phenomenon point does not change
                # TODO perhaps move the phenomenon point of reference

        # All terrain affordances are always added
        if affordance.experience.type in TERRAIN_EXPERIENCE_TYPES:
            affordance.point = np.array(affordance.point - self.point, dtype=int)
            # TODO Perhaps clone the affordance
            position_correction = np.array([0, 0, 0], dtype=int)
            self.affordances.append(affordance)
            if affordance.experience.type == EXPERIENCE_FLOOR:
                if affordance.is_similar_to(self.origin_affordance):
                    # Correct the robot's position
                    # position_correction = self.origin_affordance.point - affordance.point
                    print("Near origin affordance")
                    position_correction = self.origin_affordance.color_position(affordance.experience.color_index) - affordance.point

                    # Correct the position of the affordances
                    print("Origin affordance clock:", self.origin_affordance.experience.clock)
                    print("Current Affordance clock", affordance.experience.clock)
                    for a in [a for a in self.affordances if a.experience.clock > self.origin_affordance.experience.clock]:
                        coef = (a.experience.clock - self.origin_affordance.experience.clock)/(affordance.experience.clock - self.origin_affordance.experience.clock)
                        ac = np.array(position_correction * coef, dtype=int)
                        a.point += ac
                        print("Affordance clock:", a.experience.clock, "corrected by:", ac, "coef:", coef)

                    # affordance.point += position_correction
            return position_correction
        # No position correction
        return None  # Must return None to check if this affordance can be associated with another phenomenon

    def save(self, experiences):
        """Return a clone of the phenomenon for memory snapshot"""
        # Use the experiences cloned when saving egocentric memory
        saved_phenomenon = PhenomenonTerrain(self.origin_affordance)
        super().save(saved_phenomenon, experiences)
        return saved_phenomenon

