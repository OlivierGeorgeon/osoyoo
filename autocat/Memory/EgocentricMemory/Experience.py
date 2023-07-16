import math
import numpy as np
from pyrr import matrix44, quaternion, Quaternion
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
EXPERIENCE_ROBOT = 'Robot'
FLOOR_COLORS = {0: 'LightSlateGrey', 1: 'red', 2: 'darkOrange', 3: 'gold', 4: 'limeGreen', 5: 'deepSkyBlue',
                6: 'orchid', 7: 'deepPink'}


class Experience:
    """Experiences are instances of interactions
    along with the spatial and temporal information of where and when they were enacted"""

    def __init__(self, point, experience_type, body_direction_rad, clock, experience_id, durability=10, color_index=0, direction_quaternion=Quaternion([0,0,0,1])):
        """Create an experience to be placed in the memory.
        Args:
        x, y : coordinates relative the robot.
        type : type of experience (i.e. Chock, Block, Echolocalisation, Line etc)
        durability : durability of the experience, when it reach zero the experience should be removed from the memory.
        """
        self.point = np.array(point)
        self.type = experience_type
        self.absolute_direction_rad = body_direction_rad
        self.absolute_direction_quaternion = Quaternion.from_z_rotation(body_direction_rad)
        self.clock = clock
        self.id = experience_id
        self.durability = durability
        self.color_index = color_index

        # The position matrix will cumulate the rotation and translations of the robot
        # Used to compute the position of the experience relative to the robot in egocentric memory
        direction_matrix = matrix44.create_from_inverse_of_quaternion(direction_quaternion)
        # self.position_matrix = matrix44.create_from_translation(self.point).astype('float64')
        self.position_matrix = matrix44.multiply(direction_matrix,
                                                     matrix44.create_from_translation(self.point).astype('float64'))
        # The position of the robot relative to the experience
        # Used to compute the position of the robot relative to the experience
        relative_sensor_point = -self.point.copy()  # By default the center of the robot.
        # The absolute direction of this experience

        if self.type in [EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_CENTRAL_ECHO]:
            # The position of the echo incorporating the rotation from the head
            head_direction_rad = math.atan2(point[1], point[0] - ROBOT_HEAD_X)
            self.absolute_direction_rad += head_direction_rad  # The absolute direction of the sensor...
            self.absolute_direction_quaternion *= Quaternion.from_z_rotation(head_direction_rad)
            self.absolute_direction_rad = np.mod(self.absolute_direction_rad, 2*math.pi)  # ...within [0,2pi]
            translation_from_head_matrix = matrix44.create_from_translation([math.sqrt((point[0]-ROBOT_HEAD_X)**2 + point[1]**2),
                                                                             0, 0])
            position_from_head_matrix = matrix44.multiply(translation_from_head_matrix,
                                                          matrix44.create_from_z_rotation(-head_direction_rad))
            # The position matrix initialized with rotation from the head rather than from the center of the robot
            self.position_matrix = matrix44.multiply(position_from_head_matrix,
                                                     matrix44.create_from_translation([ROBOT_HEAD_X, 0, 0])
                                                     .astype('float64'))
            # The position of the head relative to the echo in allocentric coordinates
            relative_sensor_point = np.array([-point[0] + ROBOT_HEAD_X, -point[1], 0])

        # The allocentric position of the sensor relative to the allocentric position of the experience
        body_direction_matrix = matrix44.create_from_z_rotation(-body_direction_rad)
        self._sensor_point = matrix44.apply_to_vector(body_direction_matrix, relative_sensor_point).astype(int)
        angle_sensor = math.atan2(self._sensor_point[1], self._sensor_point[0])
        self.rotation_matrix = matrix44.create_from_z_rotation(math.pi - angle_sensor)

    def __str__(self):
        return "(id:" + str(self.id) + ",clock:" + str(self.clock) + ", type:" + self.type + ")"

    def body_direction_quaternion(self):
        """Return the quaternion representing the body direction"""
        return self.absolute_direction_quaternion
        # return quaternion.create_from_z_rotation(self.absolute_direction_rad)

    def displace(self, displacement_matrix):
        """Displace the experience by the displacement_matrix"""
        # Update the position matrix in robot-centric coordinates
        # by miraculously multiplying the position_matrix by the displacement_matrix
        self.position_matrix = matrix44.multiply(self.position_matrix, displacement_matrix)

        # Recompute the experience's coordinates in egocentric coordinates
        self.point = matrix44.apply_to_vector(self.position_matrix, [0, 0, 0])

    def sensor_point(self):
        """Return a clone of the sensor point relative to the experience"""
        return self._sensor_point.copy()

    def save(self):
        """Create a copy of the experience for memory snapshot"""
        saved_experience = Experience(self.point, self.type, self.absolute_direction_rad, self.clock,
                                      self.id, self.durability, self.color_index)
        # Clone the position matrix so it can be updated separately
        saved_experience.position_matrix = self.position_matrix.copy()
        # Reset the absolute directions  TODO Modify so they don't have to be reset
        saved_experience.absolute_direction_rad = self.absolute_direction_rad
        saved_experience._sensor_point = self.sensor_point()  # The cloned experience would compute from the new x y
        saved_experience.rotation_matrix = self.rotation_matrix
        return saved_experience
