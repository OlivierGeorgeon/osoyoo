import numpy as np
from pyrr import matrix44, Quaternion, Vector3
from ...Robot.RobotDefine import ROBOT_HEAD_X, ROBOT_COLOR_SENSOR_X, ROBOT_FLOOR_SENSOR_X

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
EXPERIENCE_TOUCH = 'touch'
EXPERIENCE_COMPASS = 'Compass'
EXPERIENCE_AZIMUTH = 'Azimuth'
FLOOR_COLORS = {0: 'LightSlateGrey', 1: 'red', 2: 'darkOrange', 3: 'gold', 4: 'limeGreen', 5: 'deepSkyBlue',
                6: 'orchid', 7: 'deepPink'}


class Experience:
    """Experiences are instances of interactions
    along with the spatial and temporal information of where and when they were enacted"""

    def __init__(self, pose_matrix, experience_type, clock, experience_id, durability=10, color_index=0):
        """Create an experience to be placed in the memory.
        Args:
        point : position of the affordance relative to the robot.
        type : type of experience (i.e. Chock, Block, Echolocalisation, Line etc)
        durability : durability of the experience, when it reach zero the experience should be removed from the memory.
        """
        self.pose_matrix = pose_matrix
        self.type = experience_type
        self.clock = clock
        self.id = experience_id
        self.durability = durability
        self.color_index = color_index

    def __str__(self):
        return "(id:" + str(self.id) + ",clock:" + str(self.clock) + ", type:" + self.type + ")"

    def displace(self, displacement_matrix):
        """Displace the experience by the displacement_matrix"""
        # by miraculously multiplying the position_matrix by the displacement_matrix
        self.pose_matrix = matrix44.multiply(self.pose_matrix, displacement_matrix)

    def point(self):
        """Return the point of reference of this point of interest. Used for compass calibration"""
        # Translate the origin point by the pose
        return matrix44.apply_to_vector(self.pose_matrix, [0., 0., 0.])

    def absolute_quaternion(self, body_quaternion):
        """Return a quaternion representing the absolute direction of this experience"""
        # The body quaternion minus the relative direction of the experience
        return Quaternion.from_matrix(self.pose_matrix).inverse * body_quaternion

    def polar_sensor_point(self, body_quaternion):
        """Return the polar-egocentric position of the sensor relative to this experience"""
        # The position of the center of the robot
        ego_robot_center = -Vector3(self.point())
        if self.type in [EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_CENTRAL_ECHO]:
            # The position of the head relative to the echo
            return body_quaternion * (ego_robot_center + [ROBOT_HEAD_X, 0, 0])
        elif self.type == EXPERIENCE_FLOOR:
            # The position of the color sensor at the end of the interaction relative to the experience
            return body_quaternion * (ego_robot_center + [ROBOT_COLOR_SENSOR_X, 0, 0])
        else:
            # The other sensors are at the position of the experience
            return Vector3([0, 0, 0])
            # return body_quaternion * ego_robot_center

    def save(self):
        """Create a copy of the experience for memory snapshot"""
        # Clone the position matrix so it can be updated separately
        return Experience(self.pose_matrix.copy(), self.type, self.clock, self.id, self.durability,
                          self.color_index)
