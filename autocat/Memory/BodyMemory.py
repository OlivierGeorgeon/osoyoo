import math
import numpy as np
from pyrr import matrix44
from ..Robot.RobotDefine import ROBOT_FRONT_X, ROBOT_SIDE
from ..Utils import assert_almost_equal_angles


class BodyMemory:
    """Memory of body position"""
    def __init__(self, ):
        """Initialize the body position and speed variables"""
        self.head_direction_rad = .0  # [-pi/2, pi/2] Radian relative to the robot's x axis
        self.body_direction_rad = .0  # [-pi, pi] Radian relative to horizontal x axis (west-east)

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
        self.body_direction_rad = math.radians(body_direction_degree)

    def body_azimuth(self):
        """Return the azimuth in degree relative to north [0,360["""
        return round((90 - math.degrees(self.body_direction_rad)) % 360)

    def body_direction_degree(self):
        """Return the body direction in degree relative to the x axis [-180,180["""
        return round(math.degrees(self.body_direction_rad))

    def body_direction_matrix(self):
        """Return the opposite body direction matrix to apply to experiences"""
        return matrix44.create_from_z_rotation(-self.body_direction_rad)

    def rotate_degree(self, yaw_degree: int, compass_azimuth: int):
        """Rotate the robot's body by the yaw and correct drift using azimuth if out of bound."""
        # Integrate the azimuth from the yaw
        azimuth = self.body_azimuth() - yaw_degree  # Yaw is counterclockwise
        azimuth %= 360

        # If integrated azimuth is too far from the compass azimuth then use the compass azimuth
        if compass_azimuth > 0:  # Don't apply if imu has no compass information
            # if 10 < abs(azimuth - compass_azimuth) < 350:  # More than 350 means both close to north
            if not assert_almost_equal_angles(math.radians(azimuth), math.radians(compass_azimuth), 10):
                azimuth = compass_azimuth

        self.set_body_direction_from_azimuth(azimuth)

    def head_absolute_direction(self):
        return self.body_direction_rad + self.head_direction_rad

    def outline(self):
        """The rectangle occupied by the robot's body - North up"""
        # outline = [[ROBOT_FRONT_X, ROBOT_SIDE, 0], [-ROBOT_FRONT_X, ROBOT_SIDE, 0],
        #            [-ROBOT_FRONT_X, -ROBOT_SIDE, 0], [ROBOT_FRONT_X, -ROBOT_SIDE, 0]]
        # return matrix44.apply_to_vector(self.body_direction_matrix(), outline)
        # Apply to array of vectors is not working:
        # Pyrr 0.10.3 installed different from https://github.com/adamlwgriffiths/Pyrr/blob/master/pyrr/matrix44.py
        p1 = matrix44.apply_to_vector(self.body_direction_matrix(), [ROBOT_FRONT_X, ROBOT_SIDE, 0])
        p2 = matrix44.apply_to_vector(self.body_direction_matrix(), [-ROBOT_FRONT_X, ROBOT_SIDE, 0])
        p3 = matrix44.apply_to_vector(self.body_direction_matrix(), [-ROBOT_FRONT_X, -ROBOT_SIDE, 0])
        p4 = matrix44.apply_to_vector(self.body_direction_matrix(), [ROBOT_FRONT_X, -ROBOT_SIDE, 0])

        return np.array([p1, p2, p3, p4])
