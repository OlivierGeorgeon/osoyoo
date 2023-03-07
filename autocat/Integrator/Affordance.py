import math
from pyrr import matrix44
from ..Memory.EgocentricMemory.Experience import EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_CENTRAL_ECHO
from ..Utils import assert_almost_equal_angles

MAX_SIMILAR_DISTANCE = 300  # (mm) Max distance within which affordances are similar
MAX_SIMILAR_DIRECTION = 15  # (degrees) Max angle within which affordances are similar
MIN_OPPOSITE_DIRECTION = 135  # (degrees) Min angle to tell affordances are in opposite directions


class Affordance:
    """An affordance is an experience localized relative to a phenomenon"""
    def __init__(self, point, experience):
        """Position should be integer to facilitate search"""
        self.point = point
        self.experience = experience

    def is_similar_to(self, other_affordance):
        """Affordances are similar if they have similar point and their experience have similar absolute direction"""
        if math.dist(self.point, other_affordance.point) < MAX_SIMILAR_DISTANCE:
            if assert_almost_equal_angles(self.experience.absolute_direction_rad,
                                          other_affordance.experience.absolute_direction_rad,
                                          MAX_SIMILAR_DIRECTION):
                # print("Near affordance: point 1:", self.point, ", point 2:", other_affordance.point,
                #       ", direction 1: ", round(math.degrees(self.experience.absolute_direction_rad)),
                #       "°, direction 2: ", round(math.degrees(other_affordance.experience.absolute_direction_rad)), "°")
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
        """The set of points to display the sensor in phenomenon view"""
        points = None
        if self.experience.type in [EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_CENTRAL_ECHO]:
            # The position of the sensor
            p1 = matrix44.apply_to_vector(self.experience.sensor_matrix, [0, 0, 0])
            # Second point of the triangle
            orthogonal_rotation = matrix44.create_from_z_rotation(math.pi/2)
            p2_matrix = matrix44.multiply(self.experience.sensor_matrix, orthogonal_rotation)
            p2_matrix[3, 0] *= 0.4
            p2_matrix[3, 1] *= 0.4
            p2 = matrix44.apply_to_vector(p2_matrix, [0, 0, 0])
            # Third point of the triangle
            p3_matrix = matrix44.multiply(self.experience.sensor_matrix, orthogonal_rotation)
            p3_matrix[3, 0] *= -0.4
            p3_matrix[3, 1] *= -0.4
            p3 = matrix44.apply_to_vector(p3_matrix, [0, 0, 0])

            # Add the position of the affordance to the position of the triangle
            points = [p1, p2, p3] + self.point
        return points

    def save(self, experience):
        """Return a cloned affordance for memory snapshot"""
        # Use the experience cloned when saving egocentric memory
        return Affordance(self.point.copy(), experience)
