import numpy as np
import math
from pyrr import matrix44
from .Phenomenon import Phenomenon
from autocat.Memory.EgocentricMemory.Experience import EXPERIENCE_PLACE, EXPERIENCE_FLOOR


TERRAIN_EXPERIENCE_TYPES = [EXPERIENCE_PLACE, EXPERIENCE_FLOOR]
# ABS = -1  # The key for the absolute origin affordance


class PhenomenonTerrain(Phenomenon):
    """A hypothetical phenomenon related to floor detection"""
    def __init__(self, affordance):
        super().__init__(affordance)
        # print("New phenomenon terrain with experience clock:", affordance.experience.clock)
        self.confidence = 0.1  # Must not be null to allow position correction
        # If the affordance is color floor then use it as absolute origin
        if affordance.absolute_point_interest():
            self.absolute_affordance_key = 0
            # self.affordances[ABS] = affordance
            # del self.affordances[0]
            self.last_origin_clock = affordance.experience.clock

    # def is_absolute_point(self, affordance):
    #     """Return True if this affordance can be used as absolute origin of this phenomenon"""
    #     return affordance.experience.type == EXPERIENCE_FLOOR and affordance.experience.color_index > 0

    def update(self, affordance):
        """Test if the affordance is within the acceptable delta from the position of the phenomenon,
        if yes, add the affordance to the phenomenon, and return the robot's position correction."""

        # Check if the affordance is acceptable for this phenomenon type
        if affordance.experience.type in TERRAIN_EXPERIENCE_TYPES:
            # Add the affordance
            affordance.point = affordance.point.astype(int) - self.point.astype(int)
            self.affordance_id += 1
            self.affordances[self.affordance_id] = affordance
            position_correction = np.array([0, 0, 0], dtype=int)
            # If the phenomenon does not have an absolute origin yet
            if self.absolute_affordance_key is None:
                if affordance.absolute_point_interest():
                    # This experience becomes the phenomenon's absolute origin
                    # delta = affordance.point.astype(int) - self.point.astype(int)
                    self.point += affordance.point #.copy().astype(int)
                    # All the position of affordance including this one are adjusted
                    for a in self.affordances.values():
                        a.point -= affordance.point
                    # The position of this affordance is reset
                    # affordance.point = np.array([0, 0, 0], dtype=int)
                    self.absolute_affordance_key = self.affordance_id
                    self.last_origin_clock = affordance.experience.clock
                # else:
                    # Simply add this affordance
                    # affordance.point = affordance.point - self.point
                    # self.affordance_id += 1
                    # self.affordances[self.affordance_id] = affordance
                    return position_correction
            # If this phenomenon has an absolute origin
            else:
                # affordance.point = np.array(affordance.point - self.point, dtype=int)
                # affordance.point = affordance.point - self.point
                # self.affordance_id += 1
                # self.affordances[self.affordance_id] = affordance
                # If this affordance is similar to the origin
                if affordance.experience.type == EXPERIENCE_FLOOR and affordance.is_similar_to(self.absolute_affordance()):
                    # Correct the robot's position
                    print("Near absolute origin affordance")
                    position_correction = self.absolute_affordance().color_position(affordance.experience.color_index) \
                        - affordance.point

                    # Correct the position of the affordances since last time the robot visited the absolute origin
                    print("Last origin clock:", self.last_origin_clock)
                    print("Current Affordance clock", affordance.experience.clock)
                    for a in [a for a in self.affordances.values() if a.experience.clock > self.last_origin_clock]:
                        coef = (a.experience.clock - self.last_origin_clock)/(affordance.experience.clock - self.last_origin_clock)
                        ac = np.array(position_correction * coef, dtype=int)
                        a.point += ac
                        print("Affordance clock:", a.experience.clock, "corrected by:", ac, "coef:", coef)
                    self.last_origin_clock = affordance.experience.clock
                    # affordance.point += position_correction
            return position_correction
        # No position correction
        return None  # Must return None to check if this affordance can be associated with another phenomenon

    def origin_prompt(self):
        """Return the position where to go to check the origin"""
        return self.absolute_affordance().experience.sensor_point() + self.point

    def confirmation_prompt(self):
        """Return the point to aim at for confirmation of this phenomenon"""
        if self.absolute_affordance() is not None:
            rotation_matrix = self.absolute_affordance().experience.rotation_matrix
            point = np.array([500, 0, 0])
            print("Computing confirmation point from origin", self.point)
            confirmation_point = matrix44.apply_to_vector(rotation_matrix, point).astype(int) + self.point
            return confirmation_point
        return None

    def phenomenon_label(self):
        """Return the text to display in phenomenon view"""
        if self.absolute_affordance() is not None:
            label = "Origin: " + str(self.point[0]) + "," + str(self.point[1]) + " Relative origin prompt: " + \
                    str(self.absolute_affordance().experience.sensor_point())
        else:
            label = "Origin: " + str(self.point) + \
                    str(self.affordances[0].experience.sensor_point())
        return label

    def save(self, experiences):
        """Return a clone of the phenomenon for memory snapshot"""
        # Use the experiences cloned when saving egocentric memory
        # if self.absolute_affordance() is not None:
        #     saved_phenomenon = PhenomenonTerrain(self.affordances[ABS].save(experiences))
        # else:
        saved_phenomenon = PhenomenonTerrain(self.affordances[0].save(experiences))
        super().save(saved_phenomenon, experiences)
        return saved_phenomenon

