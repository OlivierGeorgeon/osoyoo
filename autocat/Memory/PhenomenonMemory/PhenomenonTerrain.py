import numpy as np
from pyrr import matrix44
from .Phenomenon import Phenomenon
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_PLACE, EXPERIENCE_FLOOR
from ...Robot.RobotDefine import TERRAIN_RADIUS


TERRAIN_EXPERIENCE_TYPES = [EXPERIENCE_PLACE, EXPERIENCE_FLOOR]
TERRAIN_INITIAL_CONFIDENCE = 0.1  # Must not be null to allow position correction
TERRAIN_ORIGIN_CONFIDENCE = 0.2  # When the robot emits its position in the message


class PhenomenonTerrain(Phenomenon):
    """A hypothetical phenomenon related to floor detection"""
    def __init__(self, affordance):
        super().__init__(affordance)
        # print("New phenomenon terrain with experience clock:", affordance.experience.clock)
        self.confidence = TERRAIN_INITIAL_CONFIDENCE
        # If the affordance is color floor then use it as absolute origin
        self.interpolation_types = [EXPERIENCE_FLOOR]
        if affordance.absolute_point_interest():
            self.absolute_affordance_key = 0
            self.last_origin_clock = affordance.experience.clock

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

            # Check if this affordance is absolute
            if affordance.absolute_point_interest():
                # If the phenomenon does not have an absolute origin yet then this affordance becomes the absolute
                if self.absolute_affordance_key is None:
                    # This experience becomes the phenomenon's absolute origin
                    self.absolute_affordance_key = self.affordance_id
                    self.last_origin_clock = affordance.experience.clock
                    # The phenomenon's origin moves to the green patch relative to this affordance
                    self.point += affordance.color_position()
                    if affordance.experience.sensor_point()[0] < 0:
                        terrain_offset = np.array(TERRAIN_RADIUS)
                    else:
                        terrain_offset = -np.array(TERRAIN_RADIUS)
                    self.point -= terrain_offset
                    # All the position of affordance including this one are adjusted
                    for a in self.affordances.values():
                        a.point -= affordance.color_position()
                        a.point += terrain_offset
                    self.confidence = TERRAIN_ORIGIN_CONFIDENCE
                else:
                    position_correction = - affordance.color_position()
                    # If the origin affordance has the opposite orientation then we assume it is the other color patch
                    # if np.dot(affordance.experience.sensor_point(), self.affordances[self.absolute_affordance_key].experience.sensor_point()) < 0:
                    #     # If the affordance sensor point is negative then it is the South-West patch
                    #     print("Affordance sensor point", affordance.experience.sensor_point())
                    if affordance.experience.sensor_point()[0] < 0:
                        position_correction += np.array(TERRAIN_RADIUS)
                    else:
                        # The North-East patch
                        position_correction -= np.array(TERRAIN_RADIUS)
                    # Correct the position of the affordances since last time the robot visited the absolute origin
                    # print("Last origin clock:", self.last_origin_clock)
                    # print("Current Affordance clock", affordance.experience.clock)
                    for a in [a for a in self.affordances.values() if a.experience.clock > self.last_origin_clock]:
                        coef = (a.experience.clock - self.last_origin_clock)/(affordance.experience.clock
                                                                              - self.last_origin_clock)
                        ac = np.array(position_correction * coef, dtype=int)
                        a.point += ac
                        print("Affordance clock:", a.experience.clock, "corrected by:", ac, "coef:", coef)
                    self.last_origin_clock = affordance.experience.clock

            # Interpolate the outline
            self.convex_hull()
            self.interpolate()
            return position_correction
        # Affordances that do not belong to this phenomenon must return None
        return None

    def origin_point(self):
        """Return the position where to go to check the origin"""
        if self.absolute_affordance() is not None:
            return self.absolute_affordance().point + self.point
                # self.absolute_affordance().experience.sensor_poi8nt() + self.point
        else:
            return None

    def confirmation_prompt(self):
        """Return the point in polar egocentric coordinates to aim for confirmation of this phenomenon"""
        # Parallel to the absolute affordance direction
        if self.absolute_affordance() is not None:
            rotation_matrix = self.absolute_affordance().experience.rotation_matrix
            point = np.array([-500, 0, 0])  # Need the opposite
            # print("Computing confirmation point from origin", self.point)
            confirmation_point = matrix44.apply_to_vector(rotation_matrix, point).astype(int) + self.point
            return confirmation_point
        return None

    def outline(self):
        return self.interpolation_points
        # return self.interpolate(EXPERIENCE_FLOOR)

    def phenomenon_label(self):
        """Return the text to display in phenomenon view"""
        label = "Origin: " + str(self.point[0]) + "," + str(self.point[1])
        return label

    def save(self, experiences):
        """Return a clone of the phenomenon for memory snapshot"""
        saved_phenomenon = PhenomenonTerrain(self.affordances[0].save(experiences))
        super().save(saved_phenomenon, experiences)
        return saved_phenomenon

