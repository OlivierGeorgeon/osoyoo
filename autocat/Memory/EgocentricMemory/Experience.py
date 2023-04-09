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
COLOR_FLOOR = "LightSlateGrey"


class Experience:
    """Experiences are instances of interactions
    along with the spatial and temporal information of where and when they were enacted"""

    def __init__(self, x, y, experience_type, body_direction_rad, clock, experience_id, durability=10, color=None):
        """Create an experience to be placed in the memory.
        Args:
        x, y : coordinates relative the robot.
        type : type of experience (i.e. Chock, Block, Echolocalisation, Line etc)
        durability : durability of the experience, when it reach zero the experience should be removed from the memory.
        """
        self.point = np.array([x, y, 0])
        self.type = experience_type
        self.absolute_direction_rad = body_direction_rad
        self.clock = clock
        self.id = experience_id
        self.durability = durability
        self.color = color

        # The position matrix will cumulate the rotation and translations of the robot
        # Used to compute the position of the experience relative to the robot in egocentric memory
        self.position_matrix = matrix44.create_from_translation(self.point).astype('float64')
        # The position of the robot relative to the experience
        # Used to compute the position of the robot relative to the experience
        # opposite_position_matrix = matrix44.create_from_translation(-self.point).astype('float64')
        relative_sensor_point = -self.point  # By default the center of the robot
        # The absolute direction of this experience

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
            # The position matrix initialized with rotation from the head rather than from the center of the robot
            self.position_matrix = matrix44.multiply(position_from_head_matrix,
                                                     matrix44.create_from_translation([ROBOT_HEAD_X, 0, 0])
                                                     .astype('float64'))
            # The position of the head relative to the echo in allocentric coordinates
            # opposite_position_matrix = matrix44.create_from_translation([-x + ROBOT_HEAD_X, -y, 0])
            relative_sensor_point = np.array([-x + ROBOT_HEAD_X, -y, 0])

        # opposite azimuth
        body_direction_matrix = matrix44.create_from_z_rotation(-body_direction_rad)
        # Move the head position by the azimuth
        # sensor_matrix = matrix44.multiply(opposite_position_matrix, body_direction_matrix)
        # self.sensor_point = matrix44.apply_to_vector(sensor_matrix, [0, 0, 0])

        # The allocentric position of the sensor relative to the allocentric position of the experience
        self.sensor_point = matrix44.apply_to_vector(body_direction_matrix, relative_sensor_point)

        # The rotation matrix to display the affordance in phenomenon view
        angle_sensor = math.atan2(self.sensor_point[1], self.sensor_point[0])
        self.rotation_matrix = matrix44.create_from_z_rotation(math.pi - angle_sensor)

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
        """Create a copy of the experience for memory snapshot"""
        saved_experience = Experience(self.point[0], self.point[1], self.type, 0, self.clock, self.id, self.durability)
        # Clone the position matrix so they can be updated separately
        saved_experience.color = self.color  # At some point may need to be cloned
        saved_experience.position_matrix = self.position_matrix.copy()

        # Absolute relative sensor position do not change
        saved_experience.absolute_direction_rad = self.absolute_direction_rad
        # saved_experience.sensor_matrix = self.sensor_matrix
        saved_experience.rotation_matrix = self.rotation_matrix
        return saved_experience
