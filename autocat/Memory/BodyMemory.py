import math


class BodyMemory:
    """Memory of body position"""
    def __init__(self, ):
        self.head_direction_rad = 0  # radians relative to the robot's x axis [-pi/2, pi/2]
        self.azimuth_rad = 0  # radian relative to horizontal x axis (west-east)

    def set_head_direction_degree(self, head_direction_degree):
        """Set the head direction from degree measure"""
        assert(-90 <= head_direction_degree <= 90)
        self.head_direction_rad = math.radians(head_direction_degree)

    def head_direction_degree(self):
        """Return the robot's head direction in degrees"""
        return math.degrees(self.head_direction_rad)

    def set_azimuth_degree(self, azimuth_degree):
        """Set the azimuth from degree measure relative to north [0, 360["""
        assert(0 <= azimuth_degree < 360)
        deg_trig = 90 - azimuth_degree  # Degree relative to x axis in trigonometric direction
        while deg_trig < -180:  # Keep within [-180, 180]
            deg_trig += 360
        self.azimuth_rad = math.pi/2 - math.radians(azimuth_degree)

    def azimuth_degree(self):
        """Return the azimuth in degree relative to north"""
        deg_north = 90 - math.degrees(self.azimuth_rad)
        while deg_north < 0:  # Keep within [0, 360]
            deg_north += 360
        return deg_north
