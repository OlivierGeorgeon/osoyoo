import math
from pyrr import Quaternion


def short_angle(quaternion1, quaternion2):
    """Return the short angle from q1 to q2, positive if q2 is to the left of q1 (q2 > q1)"""
    q = quaternion1 * quaternion2.inverse
    angle = q.angle
    if angle > math.pi:  # The short angle
        angle -= 2.0 * math.pi
    elif angle < -math.pi:
        angle += 2.0 * math.pi
    if q.axis[2] > 0:  # The direction of the z axis rotation
        angle *= -1
    return angle


def assert_almost_equal_angles(angle1, angle2, difference_degrees):
    """True if the two angles (in radian) are within difference_degree"""
    # https://stackoverflow.com/questions/27255080/python-unittesting-test-whether-two-angles-are-almost-equal
    c2 = (math.sin(angle1) - math.sin(angle2)) ** 2 + (math.cos(angle1) - math.cos(angle2)) ** 2
    angle_diff = math.acos((2.0 - c2) / 2.0)
    return abs(angle_diff) < math.radians(difference_degrees)


# def rotate_vector_z(vector, angle):
#     """Return another vector 3D representing Vector rotated by Angle in trigonometric direction"""
#     # Must take the opposite angle to rotate in the trigonometric direction
#     # Apparently, pyrr uses a left-handed coordinate system:
#     # https://www.evl.uic.edu/ralph/508S98/coordinates.html
#     rotation_matrix = pyrr.Matrix44.from_z_rotation(-angle)
#     return pyrr.matrix44.apply_to_vector(rotation_matrix, vector)


# def body_direction_from_azimuth(azimuth_degree):
#     """Return the body direction from azimuth measure relative to north [0,360[ degree"""
#     body_direction_degree = 90 - azimuth_degree  # Degree relative to x axis in trigonometric direction
#     while body_direction_degree < -180:  # Keep within [-180, 180]
#         body_direction_degree += 360
#     return math.radians(body_direction_degree)

# Testing the utils
# py autocat.Utils.py
if __name__ == "__main__":
    q1 = Quaternion.from_z_rotation(math.radians(0))
    q2 = Quaternion.from_z_rotation(math.radians(10))
    print("10° to the left of 0°", short_angle(q1, q2), short_angle(q1, q2) > 0)
    q2 = Quaternion.from_z_rotation(math.radians(170))
    print("170° to the left of 0°", short_angle(q1, q2), short_angle(q1, q2) > 0)
    q2 = Quaternion.from_z_rotation(math.radians(-10))
    print("-10° to the right of 0°", short_angle(q1, q2), short_angle(q1, q2) < 0)
    q2 = Quaternion.from_z_rotation(math.radians(350))
    print("350° to the right of 0°", short_angle(q1, q2), short_angle(q1, q2) < 0)
    q2 = Quaternion.from_z_rotation(math.radians(0))
    print("0° same as 0°", short_angle(q1, q2), short_angle(q1, q2) == 0)
    q2 = Quaternion.from_z_rotation(math.radians(360))
    print("360° same as 0°", short_angle(q1, q2), short_angle(q1, q2) == 0)

    q1 = Quaternion.from_z_rotation(math.radians(90))
    q2 = Quaternion.from_z_rotation(math.radians(100))
    print("100° to the left of 90°", short_angle(q1, q2), short_angle(q1, q2) > 0)
    q2 = Quaternion.from_z_rotation(math.radians(80))
    print("80° to the right of 90°", short_angle(q1, q2), short_angle(q1, q2) < 0)

    q1 = Quaternion.from_z_rotation(math.radians(180))
    q2 = Quaternion.from_z_rotation(math.radians(190))
    print("190° to the left of 180°", short_angle(q1, q2), short_angle(q1, q2) > 0)
    q2 = Quaternion.from_z_rotation(math.radians(-170))
    print("-170° to the left of 180°", short_angle(q1, q2), short_angle(q1, q2) > 0)
    q2 = Quaternion.from_z_rotation(math.radians(170))
    print("170° to the right of 180°", short_angle(q1, q2), short_angle(q1, q2) < 0)
    q2 = Quaternion.from_z_rotation(math.radians(-190))
    print("-190° to the right of 180°", short_angle(q1, q2), short_angle(q1, q2) < 0)
