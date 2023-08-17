import math
import numpy as np
from pyrr import matrix44
from autocat.Memory.EgocentricMemory.Experience import EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_CENTRAL_ECHO, \
    EXPERIENCE_FLOOR
from autocat.Utils import assert_almost_equal_angles

MAX_SIMILAR_DISTANCE = 300    # (mm) Max distance within which affordances are similar
MAX_SIMILAR_DIRECTION = 15    # (degrees) Max angle within which affordances are similar
MIN_OPPOSITE_DIRECTION = 135  # (degrees) Min angle to tell affordances are in opposite directions
COLOR_DISTANCE = 50           # (mm) The distance between patches of colors. On A4 paper: 40mm. On A3 paper: 50mm
MIDDLE_COLOR_INDEX = 4        # (color index) The index of the middle color (green)


class Affordance:
    """An affordance is an experience localized relative to a phenomenon"""
    def __init__(self, point, experience):
        """Position should be integer to facilitate search"""
        self.point = point
        self.experience = experience

    def absolute_point_interest(self):
        """Return True if this affordance can be used as absolute origin of this phenomenon"""
        return self.experience.type == EXPERIENCE_FLOOR and self.experience.color_index > 0

    def is_similar_to(self, other_affordance):
        """Return True if the the two interactions are similar"""

        # Echo affordances
        if self.experience.type in [EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_CENTRAL_ECHO]:
            # Similar if they have similar point and their experience have similar absolute direction
            if other_affordance.experience.type in [EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_CENTRAL_ECHO]:
                if math.dist(self.point, other_affordance.point) < MAX_SIMILAR_DISTANCE:
                    if assert_almost_equal_angles(self.experience.absolute_direction_rad,
                                                  other_affordance.experience.absolute_direction_rad,
                                                  MAX_SIMILAR_DIRECTION):
                        # print("Near affordance: point 1:", self.point, ", point 2:", other_affordance.point,
                        #       ", direction 1: ", round(math.degrees(self.experience.absolute_direction_rad)),
                        #       "°, direction 2: ", round(math.degrees(other_affordance.experience.absolute_direction_rad)), "°")
                        return True
        # Floor affordances colored
        if self.experience.type == EXPERIENCE_FLOOR and self.experience.color_index > 0:
            if other_affordance.experience.type == EXPERIENCE_FLOOR and self.experience.color_index > 0:
                print("Similar Floor affordances")
                return True

        return False

    def is_opposite_to(self, other_affordance):
        """Affordances are opposite to if their absolute directions are not close to each other"""
        if not assert_almost_equal_angles(self.experience.absolute_direction_rad,
                                          other_affordance.experience.absolute_direction_rad,
                                          MIN_OPPOSITE_DIRECTION):
            print("Opposite affordance: direction 1:", round(math.degrees(self.experience.absolute_direction_rad)),
                  "°, direction 2: ", round(math.degrees(other_affordance.experience.absolute_direction_rad)), "°")
            return True
        return False

    def is_clockwise_from(self, other_affordance):
        """this affordance is in clockwise direction (within pi/4) from the other affordance in argument"""
        new_affordance_angle = self.experience.absolute_direction_rad % (2 * math.pi)
        origin_angle = other_affordance.experience.absolute_direction_rad % (2 * math.pi)
        if origin_angle > new_affordance_angle:
            if (origin_angle - new_affordance_angle) <= math.pi / 4:  # Clockwise and within pi/4
                print("Clockwise: new direction:", round(math.degrees(new_affordance_angle)),
                      "°, from origin direction: ", round(math.degrees(origin_angle)), "°")
                return True
        else:
            if (new_affordance_angle - origin_angle) >= 7 * math.pi / 4:  # 2pi-pi/4 = 315°
                print("Clockwise: new direction:", round(math.degrees(new_affordance_angle)),
                      "°, from origin direction: ", round(math.degrees(origin_angle)), "°")
                return True
        return False

    def sensor_triangle(self):
        """Return the set of points to display the echolocalization cone"""
        points = None
        if self.experience.type in [EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_CENTRAL_ECHO]:
            # The position of the head from the position of the affordance
            p1 = self.experience.sensor_point()
            # The direction of p2 is orthogonal to the direction of the sensor
            orthogonal_rotation = matrix44.create_from_z_rotation(math.pi/2)
            p2 = matrix44.apply_to_vector(orthogonal_rotation, p1) * 0.4
            # p3 is opposite to p2 from the position of the affordance
            p3 = p2 * -0.8
            # Add the position of the affordance to the position of the triangle
            points = [p1, p2, p3] + self.point
        return points

    def color_position(self):
        """Return the position of the green patch knowing the position and color of this affordance"""
        # Orthogonal vector
        om = matrix44.create_from_z_rotation(-math.pi / 2)
        vo = matrix44.apply_to_vector(om, self.experience.sensor_point()) / \
             np.linalg.norm(self.experience.sensor_point())
        # Distance along the orthogonal vector
        color_distance = np.array((MIDDLE_COLOR_INDEX - self.experience.color_index) * vo * COLOR_DISTANCE, dtype=int)
        # print("Affordance position:", self.point, "sensor point", self.experience.sensor_point(), "color index",
        #       self.experience.color_index)
        print("Relative polar-centric position of green patch", color_distance)
        return color_distance + self.point

    def save(self, experiences):
        """Return a cloned affordance for memory snapshot"""
        # Use the experiences cloned when saving egocentric memory
        # if self.experience.id not in experiences:
        #     print("Missing experience", self.experience, 'in')
        #     print(experiences)
        return Affordance(self.point.copy(), experiences[self.experience.id])
