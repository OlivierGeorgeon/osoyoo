from pyrr import matrix44
import numpy
import math
from ...Robot.RobotDefine import ROBOT_HEAD_X

EXPERIENCE_ALIGNED_ECHO = 'Echo'
EXPERIENCE_LOCAL_ECHO = 'Local_Echo'
EXPERIENCE_CENTRAL_ECHO = 'Central_Echo'
EXPERIENCE_BLOCK = 'Block'
EXPERIENCE_IMPACT = 'Shock'
EXPERIENCE_FLOOR = 'Floor'
EXPERIENCE_FOCUS = 'Focus'
EXPERIENCE_PLACE = 'Place'


class Experience:
    """Experiences are instances of interactions
    along with the spatial and temporal information of where and when they were enacted"""

    def __init__(self, x, y, experience_type, body_direction_rad, clock, durability=10, experience_id=0):
        """Create an experience to be placed in the memory.
        Args:
        x, y : coordinates relative the robot.
        type : type of experience (i.e. Chock, Block, Echolocalisation, Line etc)
        durability : durability of the experience, when it reach zero the experience should be removed from the memory.
        """
        self.x = x
        self.y = y
        self.type = experience_type
        self.clock = clock

        # The position matrix is applied to the vertices of the point_of_interest to display
        # the point of interest at the position of the experience in egocentric view
        self.position_matrix = matrix44.create_from_translation([x, y, 0]).astype('float64')
        # The position of the robot relative to the experience
        opposite_translation_matrix = matrix44.create_from_translation([-x, -y, 0]).astype('float64')
        # The absolute direction of this affordance
        self.absolute_direction_rad = body_direction_rad

        if self.type in [EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_CENTRAL_ECHO]:
            # The position of the echo incorporating the rotation from the head
            head_direction_rad = math.atan2(y, x-ROBOT_HEAD_X)
            self.absolute_direction_rad += head_direction_rad  # The absolute direction of the sensor...
            self.absolute_direction_rad = numpy.mod(self.absolute_direction_rad, 2*math.pi)  # ...within [0,2pi]
            print("Absolute direction rad:", round(math.degrees(self.absolute_direction_rad)), "°")
            translation_from_head_matrix = matrix44.create_from_translation([math.sqrt((x-ROBOT_HEAD_X)**2 + y**2),
                                                                             0, 0])
            position_from_head_matrix = matrix44.multiply(translation_from_head_matrix,
                                                          matrix44.create_from_z_rotation(-head_direction_rad))
            self.position_matrix = matrix44.multiply(position_from_head_matrix,
                                                     matrix44.create_from_translation([ROBOT_HEAD_X, 0, 0])
                                                     .astype('float64'))
            # The position of the head relative to the echo in allocentric coordinates
            opposite_translation_matrix = matrix44.create_from_translation([-x + ROBOT_HEAD_X, -y, 0])

        # opposite azimuth
        orientation_matrix = matrix44.create_from_z_rotation(-body_direction_rad)
        # Move the head position by the azimuth
        self.sensor_matrix = matrix44.multiply(opposite_translation_matrix, orientation_matrix)

        # The rotation matrix to display the experience in phenomenon view
        p1x, p1y, _ = matrix44.apply_to_vector(self.sensor_matrix, [0, 0, 0])
        angle_sensor = math.atan2(p1y, p1x)
        self.rotation_matrix = matrix44.create_from_z_rotation(math.pi - angle_sensor)  # Don't know why need flip

        self.durability = durability
        self.actual_durability = durability
        self.tick_number = 0
        self.id = experience_id

    def tick(self):
        """Updates the clock and decay of this interaction"""
        self.tick_number += 1
        self.actual_durability -= 1

    def displace(self, displacement_matrix):
        """Displace the experience by the displacement_matrix"""

        # Update the position matrix in robot-centric coordinates
        # by miraculously multiplying the position_matrix by the displacement_matrix
        self.position_matrix = matrix44.multiply(self.position_matrix, displacement_matrix)

        # Recompute the x, y coordinates in robot-centric coordinates
        self.x, self.y, _ = matrix44.apply_to_vector(self.position_matrix, [0, 0, 0])

    def allocentric_from_matrices(self, body_direction_matrix, body_position_matrix):
        """ The allocentric coordinates of the experience given the body direction and position matrices"""
        displacement_matrix = matrix44.multiply(body_direction_matrix, body_position_matrix)
        return numpy.array(matrix44.apply_to_vector(displacement_matrix, [self.x, self.y, 0]), dtype=numpy.int16)

    def allocentric_position_matrix(self, body_direction_matrix, body_position_matrix):
        """ The position matrix to place this experience in allocentric memory"""
        displacement_matrix = matrix44.multiply(body_direction_matrix, body_position_matrix)
        return matrix44.multiply(self.position_matrix, displacement_matrix)