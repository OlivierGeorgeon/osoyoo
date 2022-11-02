import math
import numpy
from pyrr import matrix44
from ..Robot.RobotDefine import ROBOT_FRONT_X, ROBOT_SIDE, FORWARD_SPEED, LATERAL_SPEED


class BodyMemory:
    """Memory of body position"""
    def __init__(self, ):
        """Initialize the body position and speed variables"""
        self.head_direction_rad = .0  # [-pi/2, pi/2] Radian relative to the robot's x axis
        self.body_direction_rad = .0  # [-pi, pi] Radian relative to horizontal x axis (west-east)

        self.forward_speed = numpy.array([FORWARD_SPEED, 0])  # Need numpy arrays to compute average
        self.backward_speed = numpy.array([-FORWARD_SPEED, 0])
        self.leftward_speed = numpy.array([0, LATERAL_SPEED])
        self.rightward_speed = numpy.array([0, -LATERAL_SPEED])

    def set_head_direction_degree(self, head_direction_degree: int):
        """Set the head direction from degree measured relative to x axis [-90,90]"""
        assert(-90 <= head_direction_degree <= 90)
        self.head_direction_rad = math.radians(head_direction_degree)

    def head_direction_degree(self):
        """Return the robot's head direction in degrees [-90,90]"""
        return int(math.degrees(self.head_direction_rad))

    def set_body_direction_from_azimuth(self, azimuth_degree: int):
        """Set the body direction from azimuth measure relative to north [0,360[ degree"""
        # assert(0 <= azimuth_degree <= 361)  #
        deg_trig = 90 - azimuth_degree  # Degree relative to x axis in trigonometric direction
        while deg_trig < -180:  # Keep within [-180, 180]
            deg_trig += 360
        # self.body_direction_rad = math.pi / 2 - math.radians(azimuth_degree)
        self.body_direction_rad = math.radians(deg_trig)

    def body_azimuth(self):
        """Return the azimuth in degree relative to north [0,360["""
        deg_north = 90 - math.degrees(self.body_direction_rad)
        while deg_north < 0:  # Keep within [0, 360]
            deg_north += 360
        return int(deg_north)

    def body_direction_degree(self):
        """Return the body direction in degree relative to the x axis [-180,180["""
        return int(math.degrees(self.body_direction_rad))

    def body_direction_matrix(self):
        """Return the opposite body direction matrix to apply to experiences"""
        return matrix44.create_from_z_rotation(-self.body_direction_rad)

    def rotate_degree(self, yaw_degree: int, compass_azimuth: int):
        """Rotate the robot's body by the yaw and correct drift using azimuth if out of bound."""
        azimuth = self.body_azimuth() - yaw_degree  # Yaw is counterclockwise
        # Keep it within [0, 360[
        while azimuth < 0:
            azimuth += 360
        azimuth = azimuth % 360

        # If the direction is too far from the azimuth then use the azimuth
        # https://stackoverflow.com/questions/1878907/how-can-i-find-the-difference-between-two-angles
        if compass_azimuth > 10:  # Don't apply if imu has no compass information
            if 10 < abs(azimuth - compass_azimuth) < 350:  # More than 350 means both close to north
                azimuth = compass_azimuth

        self.set_body_direction_from_azimuth(azimuth)

    def head_absolute_direction(self):
        return self.body_direction_rad + self.head_direction_rad

    def is_inside_robot(self, x, y):
        """Return True if the point is inside the robot.
        Use robot-centric/east-north coordinates"""
        # The four points in counterclockwise order
        x1 = ROBOT_FRONT_X * math.cos(self.body_direction_rad) - ROBOT_SIDE * math.sin(self.body_direction_rad)
        y1 = ROBOT_FRONT_X * math.sin(self.body_direction_rad) + ROBOT_SIDE * math.cos(self.body_direction_rad)
        x2 = -ROBOT_FRONT_X * math.cos(self.body_direction_rad) - ROBOT_SIDE * math.sin(self.body_direction_rad)
        y2 = -ROBOT_FRONT_X * math.sin(self.body_direction_rad) + ROBOT_SIDE * math.cos(self.body_direction_rad)
        x3 = -ROBOT_FRONT_X * math.cos(self.body_direction_rad) + ROBOT_SIDE * math.sin(self.body_direction_rad)
        y3 = -ROBOT_FRONT_X * math.sin(self.body_direction_rad) - ROBOT_SIDE * math.cos(self.body_direction_rad)
        x4 = ROBOT_FRONT_X * math.cos(self.body_direction_rad) + ROBOT_SIDE * math.sin(self.body_direction_rad)
        y4 = ROBOT_FRONT_X * math.sin(self.body_direction_rad) - ROBOT_SIDE * math.cos(self.body_direction_rad)

        # Positive distance is on the left of the line, meaning inside the polygon
        # https://stackoverflow.com/questions/2752725/finding-whether-a-point-lies-inside-a-rectangle-or-not
        d1 = (x2 - x1) * (y - y1) - (x - x1) * (y2 - y1)
        d2 = (x3 - x2) * (y - y2) - (x - x2) * (y3 - y2)
        d3 = (x4 - x3) * (y - y3) - (x - x3) * (y4 - y3)
        d4 = (x1 - x4) * (y - y4) - (x - x4) * (y1 - y4)

        # return d1 > 0 and d2 > 0 and d3 > 0 and d4 > 0

        p = numpy.array([x, y])
        p1 = numpy.array([x1, y1])
        p2 = numpy.array([x2, y2])
        p3 = numpy.array([x3, y3])
        p4 = numpy.array([x4, y4])
        d1 = numpy.dot(p2-p1, p-p1)
        d2 = numpy.dot(p2-p1, p2-p1)
        d3 = numpy.dot(p3-p2, p-p2)
        d4 = numpy.dot(p3-p2, p3-p2)
        return 0 <= d1 <= d2 and 0 <= d3 <= d4
