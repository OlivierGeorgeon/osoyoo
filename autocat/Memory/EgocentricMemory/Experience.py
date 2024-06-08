import numpy as np
from pyrr import matrix44, Quaternion, Vector3, Matrix44, Matrix33
from ...Robot.RobotDefine import ROBOT_HEAD_X, ROBOT_COLOR_SENSOR_X, ROBOT_FLOOR_SENSOR_X

EXPERIENCE_LOCAL_ECHO = 1
EXPERIENCE_CENTRAL_ECHO = 2
EXPERIENCE_BLOCK = 3
EXPERIENCE_IMPACT = 4
EXPERIENCE_FLOOR = 5
EXPERIENCE_FOCUS = 6
EXPERIENCE_PLACE = 7
EXPERIENCE_PROMPT = 8
EXPERIENCE_ROBOT = 9
EXPERIENCE_TOUCH = 10
EXPERIENCE_COMPASS = 11
EXPERIENCE_AZIMUTH = 12
EXPERIENCE_ALIGNED_ECHO = 13
FLOOR_COLORS = {0: 'LightSlateGrey', 1: 'red', 2: 'darkOrange', 3: 'gold', 4: 'limeGreen', 5: 'deepSkyBlue',
                6: 'orchid', 7: 'deepPink'}


class Experience:
    """Experiences are instances of interactions
    along with the spatial and temporal information of where and when they were enacted"""

    def __init__(self, experience_id, pose_matrix, experience_type, clock, body_quaternion, durability=10,
                 color_index=0):
        """Create an experience to be placed in the memory.
        Args:
        point : position of the affordance relative to the robot.
        type : type of experience (i.e. Chock, Block, Echolocalisation, Line etc)
        durability : durability of the experience, when it reach zero the experience should be removed from the memory.
        :param body_quaternion:
        """
        self.id = experience_id
        self.pose_matrix = pose_matrix
        self.type = experience_type
        self.clock = clock
        self.body_quaternion = body_quaternion.copy()  # Used to place the experience in Place Cell
        self.durability = durability
        self.color_index = color_index

    def __str__(self):
        return f"(id:{self.id}, clock:{self.clock}, type:{self.type}, color_index:{self.color_index})"

    def displace(self, displacement_matrix):
        """Displace the experience by the displacement_matrix"""
        # By miraculously multiplying the position_matrix by the displacement_matrix
        self.pose_matrix = matrix44.multiply(self.pose_matrix, displacement_matrix)

    def point(self):
        """Return the point of this experience in egocentric coordinates."""
        # Translate the origin point by the pose
        return matrix44.apply_to_vector(self.pose_matrix, [0., 0., 0.])

    def polar_pose_matrix(self):
        """Return the pose matrix in polar centric coordinates (rotated by the body_quaternion)"""
        return Matrix44(self.body_quaternion.inverse) * self.pose_matrix

    def absolute_quaternion(self):
        """Return a quaternion representing the absolute direction of this experience"""
        # The body quaternion minus the relative direction of the experience
        return Quaternion.from_matrix(self.pose_matrix).inverse * self.body_quaternion

    def polar_sensor_point(self):
        """Return the polar-egocentric position of the sensor relative to this experience"""
        # The position of the center of the robot
        ego_robot_center = -Vector3(self.point())
        if self.type in [EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_CENTRAL_ECHO]:
            # The position of the head relative to the echo
            return self.body_quaternion * (ego_robot_center + [ROBOT_HEAD_X, 0, 0])
        elif self.type == EXPERIENCE_FLOOR:
            # The position of the color sensor at the end of the interaction relative to the experience
            return self.body_quaternion * (ego_robot_center + [ROBOT_COLOR_SENSOR_X, 0, 0])
        else:
            # The other sensors are at the position of the experience
            return Vector3([0, 0, 0])

    def save(self):
        """Create a copy of the experience for memory snapshot"""
        # Clone the position matrix so it can be updated separately
        return Experience(self.id, self.pose_matrix.copy(), self.type, self.clock, self.body_quaternion,
                          self.durability, self.color_index)
