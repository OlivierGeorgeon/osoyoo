import math
import numpy as np
from pyrr import matrix44, quaternion, Quaternion
from ..Robot.RobotDefine import ROBOT_SETTINGS, ROBOT_FRONT_X, ROBOT_SIDE


class BodyMemory:
    """Memory of body position"""
    def __init__(self, robot_id):
        """Initialize the body position and speed variables"""
        self.robot_id = robot_id
        self.head_direction_rad = .0  # [-pi/2, pi/2] Radian relative to the robot's x axis
        # self.body_quaternion = quaternion.create_from_z_rotation(0)  # The quaternion defining the direction of the body
        self.body_quaternion = Quaternion.from_z_rotation(0)  # The quaternion defining the direction of the body
        self.compass_offset = np.array(ROBOT_SETTINGS[robot_id]["compass_offset"], dtype=int)

    def set_head_direction_degree(self, head_direction_degree: int):
        """Set the head direction from degree measured relative to x axis [-90,90]"""
        assert(-90 <= head_direction_degree <= 90)
        self.head_direction_rad = math.radians(head_direction_degree)

    def head_direction_degree(self):
        """Return the robot's head direction in degrees [-90,90]"""
        return int(math.degrees(self.head_direction_rad))

    def set_body_direction_from_azimuth(self, azimuth_degree: int):
        """Set the body direction from azimuth measure relative to north [0,360[ degree"""
        body_direction_degree = 90 - azimuth_degree  # Degree relative to x axis in trigonometric direction
        while body_direction_degree < -180:  # Keep within [-180, 180]
            body_direction_degree += 360
        self.body_quaternion = quaternion.create_from_z_rotation(math.radians(body_direction_degree))

    def body_azimuth(self):
        """Return the azimuth in degree relative to north [0,360["""
        return round((90 - math.degrees(self.get_body_direction_rad())) % 360)

    def get_body_direction_rad(self):
        """Return the body direction ind rad ]-pi,pi]"""
        # The Z component of the rotation axis gives the sign of the direction
        return quaternion.rotation_axis(self.body_quaternion)[2] * quaternion.rotation_angle(self.body_quaternion)

    def body_direction_degree(self):
        """Return the body direction in degree relative to the x axis [-180,180["""
        return round(math.degrees(self.get_body_direction_rad()))

    def body_direction_matrix(self):
        """Return the body direction matrix to apply to experiences"""
        # For some reason the matrix must be the inverse of the angle and also of the quaternion
        return matrix44.create_from_inverse_of_quaternion(self.body_quaternion)
        # opposite direction because pyrr is left-handed
        # return matrix44.create_from_z_rotation(-self.get_body_direction_rad())

    def head_absolute_direction(self):
        return self.get_body_direction_rad() + self.head_direction_rad

    def outline(self):
        """The rectangle occupied by the robot's body - North up"""
        # outline = [[ROBOT_FRONT_X, ROBOT_SIDE, 0], [-ROBOT_FRONT_X, ROBOT_SIDE, 0],
        #            [-ROBOT_FRONT_X, -ROBOT_SIDE, 0], [ROBOT_FRONT_X, -ROBOT_SIDE, 0]]
        # matrix44.apply_to_vector(self.body_direction_matrix(), outline)
        # Apply to array of vectors is not working:
        # Pyrr 0.10.3 installed different from https://github.com/adamlwgriffiths/Pyrr/blob/master/pyrr/matrix44.py
        # p1 = matrix44.apply_to_vector(self.body_direction_matrix(), [ROBOT_FRONT_X, ROBOT_SIDE, 0])
        # p2 = matrix44.apply_to_vector(self.body_direction_matrix(), [-ROBOT_FRONT_X, ROBOT_SIDE, 0])
        # p3 = matrix44.apply_to_vector(self.body_direction_matrix(), [-ROBOT_FRONT_X, -ROBOT_SIDE, 0])
        # p4 = matrix44.apply_to_vector(self.body_direction_matrix(), [ROBOT_FRONT_X, -ROBOT_SIDE, 0])
        p1 = quaternion.apply_to_vector(self.body_quaternion, [ROBOT_FRONT_X, ROBOT_SIDE, 0])
        p2 = quaternion.apply_to_vector(self.body_quaternion, [-ROBOT_FRONT_X, ROBOT_SIDE, 0])
        p3 = quaternion.apply_to_vector(self.body_quaternion, [-ROBOT_FRONT_X, -ROBOT_SIDE, 0])
        p4 = quaternion.apply_to_vector(self.body_quaternion, [ROBOT_FRONT_X, -ROBOT_SIDE, 0])

        return np.array([p1, p2, p3, p4])

    def save(self):
        """Return a clone of bodymemory to save a snapshot of memory"""
        saved_body_memory = BodyMemory(self.robot_id)
        saved_body_memory.head_direction_rad = self.head_direction_rad
        # saved_body_memory.body_direction_rad = self.body_direction_rad
        saved_body_memory.body_quaternion = self.body_quaternion.copy()
        saved_body_memory.compass_offset = self.compass_offset.copy()
        return saved_body_memory
