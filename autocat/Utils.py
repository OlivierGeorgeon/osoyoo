import math
import pyrr


def assert_almost_equal_angles(angle1, angle2, difference_degrees):
    """True if the two angles (in radian) are within difference_degree"""
    # https://stackoverflow.com/questions/27255080/python-unittesting-test-whether-two-angles-are-almost-equal
    c2 = (math.sin(angle1) - math.sin(angle2)) ** 2 + (math.cos(angle1) - math.cos(angle2)) ** 2
    angle_diff = math.acos((2.0 - c2) / 2.0)
    return abs(angle_diff) < math.radians(difference_degrees)


def rotate_vector_z(vector, angle):
    """Return another vector 3D representing Vector rotated by Angle in trigonometric direction"""
    # Must take the opposite angle to rotate in the trigonometric direction
    # Apparently, pyrr uses a left-handed coordinate system:
    # https://www.evl.uic.edu/ralph/508S98/coordinates.html
    rotation_matrix = pyrr.Matrix44.from_z_rotation(-angle)
    return pyrr.matrix44.apply_to_vector(rotation_matrix, vector)
