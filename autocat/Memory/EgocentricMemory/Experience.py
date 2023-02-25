from pyrr import matrix44
import numpy as np
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
EXPERIENCE_PROMPT = 'Prompt'


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
        self.point = np.array([x, y, 0])
        self.type = experience_type
        self.clock = clock

        # The position matrix is applied to the vertices of the point_of_interest to display
        # the point of interest at the position of the experience in egocentric view
        self.position_matrix = matrix44.create_from_translation(self.point).astype('float64')
        # The position of the robot relative to the experience
        opposite_translation_matrix = matrix44.create_from_translation(-self.point).astype('float64')
        # The absolute direction of this experience
        self.absolute_direction_rad = body_direction_rad

        if self.type in [EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_CENTRAL_ECHO]:
            # The position of the echo incorporating the rotation from the head
            head_direction_rad = math.atan2(y, x-ROBOT_HEAD_X)
            self.absolute_direction_rad += head_direction_rad  # The absolute direction of the sensor...
            self.absolute_direction_rad = np.mod(self.absolute_direction_rad, 2*math.pi)  # ...within [0,2pi]
            # print("Absolute direction rad:", round(math.degrees(self.absolute_direction_rad)), "°")
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
        self.id = experience_id

    def __str__(self):
        return "(id:" + str(self.id) + ",clock:" + str(self.clock) + ")"

    def displace(self, displacement_matrix):
        """Displace the experience by the displacement_matrix"""
        # Update the position matrix in robot-centric coordinates
        # by miraculously multiplying the position_matrix by the displacement_matrix
        self.position_matrix = matrix44.multiply(self.position_matrix, displacement_matrix)

        # Recompute the experience's coordinates in robot-centric coordinates
        self.point = matrix44.apply_to_vector(self.position_matrix, [0, 0, 0])

    def save(self):
        """Create a copy of the experience to save a snapshot of memory"""
        saved_experience = Experience(self.point[0], self.point[1], self.type, 0, self.clock, self.durability, self.id)
        # Clone the position matrix so they can be updated separately
        saved_experience.position_matrix = self.position_matrix.copy()

        # Absolute relative sensor position do not change
        saved_experience.absolute_direction_rad = self.absolute_direction_rad
        saved_experience.sensor_matrix = self.sensor_matrix
        saved_experience.rotation_matrix = self.rotation_matrix
        return saved_experience
