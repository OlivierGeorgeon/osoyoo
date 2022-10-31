import math
from pyrr import matrix44, Quaternion
from ..Memory.EgocentricMemory.Experience import EXPERIENCE_ALIGNED_ECHO


class Affordance:
    """An affordance is an experience localized relative to a phenomenon"""
    def __init__(self, x, y, experience):
        self.position_matrix = matrix44.create_from_translation([x, y, 0]).astype('float64')
        self.experience = experience

        # q = Quaternion(self.experience.sensor_matrix)
        # print("Affordance " + self.experience.type + " angle: ", math.degrees(q.angle))
        # self.rotation_matrix = matrix44.create_from_z_rotation(math.pi - q.angle)

        p1x, p1y, _ = matrix44.apply_to_vector(self.experience.sensor_matrix, [0, 0, 0])
        angle_sensor = math.atan2(p1y, p1x)
        # print("Affordance " + self.experience.type + " angle: ", int(math.degrees(angle_sensor)))
        self.rotation_matrix = matrix44.create_from_z_rotation(math.pi - angle_sensor)  # Don't know why need flipping

    def sensor_triangle(self):
        """The set of points to display the sensor in phenomenon view"""
        points = None
        if self.experience.type == EXPERIENCE_ALIGNED_ECHO:
            # The position of the sensor
            sensor_position_matrix = matrix44.multiply(self.experience.sensor_matrix, self.position_matrix)
            p1x, p1y, _ = matrix44.apply_to_vector(sensor_position_matrix, [0, 0, 0])
            # Second point of the triangle
            orthogonal_rotation = matrix44.create_from_z_rotation(math.pi/2)
            p2_matrix = matrix44.multiply(self.experience.sensor_matrix, orthogonal_rotation)
            p2_matrix[3, 0] /= 3
            p2_matrix[3, 1] /= 3
            p2_matrix = matrix44.multiply(p2_matrix, self.position_matrix)
            p2x, p2y, _ = matrix44.apply_to_vector(p2_matrix, [0, 0, 0])
            # Third point of the triangle
            p3_matrix = matrix44.multiply(self.experience.sensor_matrix, orthogonal_rotation)
            p3_matrix[3, 0] /= -3
            p3_matrix[3, 1] /= -3
            p3_matrix = matrix44.multiply(p3_matrix, self.position_matrix)
            p3x, p3y, _ = matrix44.apply_to_vector(p3_matrix, [0, 0, 0])

            points = [int(p1x), int(p1y), int(p2x), int(p2y), int(p3x), int(p3y)]
        return points
