import math
import numpy as np
from pyrr import Quaternion, line, Matrix44, Vector3


def quaternion_translation_to_matrix(quaternion, translation):
    """Return the matrix that applies first rotation and second translation"""
    # Applied from right to left: rotation and then translation
    return Matrix44.from_translation(translation) * Matrix44.from_inverse_of_quaternion(quaternion)


def translation_quaternion_to_matrix(translation, quaternion):
    """Return the matrix that applies first translation and second rotation"""
    # Applied from right to left: translation and then rotation
    return Matrix44.from_inverse_of_quaternion(quaternion) * Matrix44.from_translation(translation)


def azimuth_to_quaternion(azimuth):
    """Return the quaternion representing this azimuth from north in degrees"""
    return Quaternion.from_z_rotation(math.radians(90 - azimuth))  # Wouldn't work with type int


def quaternion_to_azimuth(quaternion):
    """Return the azimuth in degree represented by this quaternion"""
    return round((90 - math.degrees(quaternion_to_direction_rad(quaternion))) % 360)


def quaternion_to_direction_rad(quaternion):
    """Return the polar-egocentric direction represented by this quaternion in [-pi, pi]"""
    # The Z component of the rotation axis gives the sign of the angle if is not NaN
    angle = quaternion.angle
    if np.isnan(angle):
        print("Angle is NaN for quaternion", repr(quaternion))
        # It printed Quaternion([0., 0., 0., 1.]) but I can't reproduce how its ".angle" is NaN
        angle = 0
    else:
        if angle > math.pi:  # The short angle
            angle -= 2.0 * math.pi
        elif angle < -math.pi:
            angle += 2.0 * math.pi
        if not np.isnan(quaternion.z) and quaternion.z < 0:  # The direction of the z axis rotation
            angle *= -1
    return angle


def length_on_line(abscissa, line1):
    """Return the length of abscissa distance projected to the line"""
    # slope = math.atan2(line1[1][1] - line1[0][1], line1[1][0] - line1[0][0])
    # # print("Slope", math.degrees(slope))
    # return x / math.cos(slope)
    length = math.sqrt((line1[1][0] - line1[0][0])**2 + (line1[1][1] - line1[0][1])**2)
    return abscissa * length / (line1[1][0] - line1[0][0])


def line_intersection(line1, line2):
    """Return the intersection of two lines in the x y plane"""
    # line1 = x1, y1, x2, y2
    x1, y1, x2, y2 = line1[0][0], line1[0][1], line1[1][0], line1[1][1]
    # line2 = x3, y3, x4, y4
    x3, y3, x4, y4 = line2[0][0], line2[0][1], line2[1][0], line2[1][1]

    determinant = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if determinant == 0:
        return np.array([0, 0, 0])  # DeciderArrange don't swipe

    intersection_x = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / determinant
    intersection_y = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / determinant
    return Vector3([intersection_x, intersection_y, 0])


def short_angle(quaternion1, quaternion2):
    """Return the short angle in radian from q1 to q2, positive if q2 is to the left of q1 (q2 > q1)"""
    return -quaternion_to_direction_rad(quaternion1 * quaternion2.inverse)


def assert_almost_equal_angles(angle1, angle2, difference_degrees):
    """True if the two angles (in radian) are within difference_degree"""
    quaternion1 = Quaternion.from_z_rotation(angle1)
    quaternion2 = Quaternion.from_z_rotation(angle2)
    return abs(short_angle(quaternion1, quaternion2)) < math.radians(difference_degrees)

    # # https://stackoverflow.com/questions/27255080/python-unittesting-test-whether-two-angles-are-almost-equal
    # c2 = (math.sin(angle1) - math.sin(angle2)) ** 2 + (math.cos(angle1) - math.cos(angle2)) ** 2
    # angle_diff = math.acos((2.0 - c2) / 2.0)
    # return abs(angle_diff) < math.radians(difference_degrees)


# Testing the utils
# py autocat\Utils.py
if __name__ == "__main__":
    # Test quaternion_to_direction_rad()
    print("=== Test quaternion_to_direction_rad(quaternion) ===")
    q = Quaternion.from_z_rotation(0)
    print("Quaternion 0 rad", quaternion_to_direction_rad(q), quaternion_to_direction_rad(q) == 0)
    q = Quaternion([0., 0., 0., 0.])
    print("Quaternion null", quaternion_to_direction_rad(q), quaternion_to_direction_rad(q) == 3.141592653589793)
    q = Quaternion.from_z_rotation(1)
    print("Quaternion 1 rad", quaternion_to_direction_rad(q), math.isclose(quaternion_to_direction_rad(q), 1))
    q = Quaternion.from_z_rotation(-1)
    print("Quaternion -1 rad", quaternion_to_direction_rad(q), math.isclose(quaternion_to_direction_rad(q), -1))
    print("")

    # Test quaternion_to_azimuth()
    print("=== Test quaternion_to_azimuth(quaternion) ===")
    q = Quaternion.from_z_rotation(0)
    print("Azimuth 0°", quaternion_to_azimuth(q), quaternion_to_azimuth(q) == 90)
    q = Quaternion.from_z_rotation(math.radians(90))
    print("Azimuth 90°", quaternion_to_azimuth(q), math.isclose(quaternion_to_azimuth(q), 0))
    q = Quaternion.from_z_rotation(math.radians(-90))
    print("Azimuth -90°", quaternion_to_azimuth(q), math.isclose(quaternion_to_azimuth(q), 180))
    q = Quaternion.from_z_rotation(math.radians(180))
    print("Azimuth 180°", quaternion_to_azimuth(q), math.isclose(quaternion_to_azimuth(q), 270))
    print("")

    # Test azimuth_to_quaternion()
    print("=== Test azimuth_to_quaternion(azimuth) ===")
    a = quaternion_to_azimuth(azimuth_to_quaternion(0))
    print("Azimuth 0°", a, a == 0)
    a = quaternion_to_azimuth(azimuth_to_quaternion(180))
    print("Azimuth 180°", a, a == 180)
    a = quaternion_to_azimuth(azimuth_to_quaternion(360))
    print("Azimuth 360°", a, a == 0)
    a = quaternion_to_azimuth(azimuth_to_quaternion(370))
    print("Azimuth 370°", a, a == 10)
    print("")

    # Test length_on_line()
    l1 = line.create_from_points([0, 1, 0], [1, 1, 0])
    # l1 = np.array([[0, 0], [1, 1]])
    print("Length of 1 on slope 0°:", length_on_line(1, l1), length_on_line(1, l1) == 1)
    l1 = line.create_from_points([0, 0, 0], [1, 1, 0])
    length_on_line(1, l1)
    print("Length of 1 on slope 45°:", length_on_line(1, l1), length_on_line(1, l1) == 1.4142135623730951)
    print("")

    # Test line_intersection()
    l1 = line.create_from_points([-1, -1, 0], [1, 1, 0])
    l2 = line.create_from_points([-1, 1, 0], [1, -1, 0])
    print("Intersection", line_intersection(l1, l2), line_intersection(l1, l2) == [0, 0, 0])
    l1 = line.create_from_points([1, 0, 0], [1, 2, 0])
    l2 = line.create_from_points([0, 1, 0], [2, 1, 0])
    print("Intersection", line_intersection(l1, l2), line_intersection(l1, l2) == [1, 1, 0])
    print("")

    # Test short_angle()
    print("=== Test short angle ===")
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

    print("=== Test yaw integration ===")
    body_quaternion = azimuth_to_quaternion(109)
    print("0 azimuth", quaternion_to_azimuth(body_quaternion))
    yaw_quaternion = Quaternion.from_z_rotation(math.radians(29))
    yaw_integration_quaternion = body_quaternion.cross(yaw_quaternion)
    compass_quaternion = azimuth_to_quaternion(89)
    if compass_quaternion.dot(yaw_integration_quaternion) < 0.0:
        yaw_integration_quaternion = - yaw_integration_quaternion
    prediction_error = math.degrees(short_angle(compass_quaternion, yaw_integration_quaternion))
    print("Rotation 29°", prediction_error, math.isclose(prediction_error, 9))
    body_quaternion = compass_quaternion.slerp(yaw_integration_quaternion, 0.75)  # 0 is yaw estimation
    print("1 azimuth", quaternion_to_azimuth(compass_quaternion), "slerp", quaternion_to_azimuth(yaw_integration_quaternion), "=", quaternion_to_azimuth(body_quaternion))

    yaw_quaternion = Quaternion.from_z_rotation(math.radians(-36))
    yaw_integration_quaternion = body_quaternion.cross(yaw_quaternion)
    compass_quaternion = azimuth_to_quaternion(110)
    if compass_quaternion.dot(yaw_integration_quaternion) < 0.0:
        yaw_integration_quaternion = - yaw_integration_quaternion
    prediction_error = math.degrees(short_angle(compass_quaternion, yaw_integration_quaternion))
    print("Rotation -36°", prediction_error, math.isclose(prediction_error, -8.249132219778671))
    body_quaternion = compass_quaternion.slerp(yaw_integration_quaternion, 0.75)  # 0.75
    print("2 azimuth", quaternion_to_azimuth(compass_quaternion), "slerp", quaternion_to_azimuth(yaw_integration_quaternion), "=", quaternion_to_azimuth(body_quaternion))

    yaw_quaternion = Quaternion.from_z_rotation(math.radians(-6))
    yaw_integration_quaternion = body_quaternion.cross(yaw_quaternion)
    compass_quaternion = azimuth_to_quaternion(124)
    if compass_quaternion.dot(yaw_integration_quaternion) < 0.0:
        yaw_integration_quaternion = - yaw_integration_quaternion
    prediction_error = math.degrees(short_angle(compass_quaternion, yaw_integration_quaternion))
    print("Rotation -6°", prediction_error, math.isclose(prediction_error, 1.8124826755303356))
    body_quaternion = compass_quaternion.slerp(yaw_integration_quaternion, 0.75)  # 0.75
    print("3 azimuth", quaternion_to_azimuth(compass_quaternion), "slerp", quaternion_to_azimuth(yaw_integration_quaternion), "=", quaternion_to_azimuth(body_quaternion))

    yaw_quaternion = Quaternion.from_z_rotation(math.radians(0))
    yaw_integration_quaternion = body_quaternion.cross(yaw_quaternion)
    compass_quaternion = azimuth_to_quaternion(125)
    if compass_quaternion.dot(yaw_integration_quaternion) < 0.0:
        yaw_integration_quaternion = - yaw_integration_quaternion
    prediction_error = math.degrees(short_angle(compass_quaternion, yaw_integration_quaternion))
    print("Rotation 0°", prediction_error, math.isclose(prediction_error, 2.3593690917011996))
    body_quaternion = compass_quaternion.slerp(yaw_integration_quaternion, 0.75)  # 0.75
    print("4 azimuth", quaternion_to_azimuth(compass_quaternion), "slerp", quaternion_to_azimuth(yaw_integration_quaternion), "=", quaternion_to_azimuth(body_quaternion))

    yaw_quaternion = Quaternion.from_z_rotation(math.radians(32))
    yaw_integration_quaternion = body_quaternion.cross(yaw_quaternion)
    compass_quaternion = azimuth_to_quaternion(83)
    if compass_quaternion.dot(yaw_integration_quaternion) < 0.0:
        yaw_integration_quaternion = - yaw_integration_quaternion
    prediction_error = math.degrees(short_angle(compass_quaternion, yaw_integration_quaternion))
    print("Rotation 32°", prediction_error, math.isclose(prediction_error, -8.230457552845197))
    body_quaternion = compass_quaternion.slerp(yaw_integration_quaternion, 0.75)  # 0.75
    print("5 azimuth", quaternion_to_azimuth(compass_quaternion), "slerp", quaternion_to_azimuth(yaw_integration_quaternion), "=", quaternion_to_azimuth(body_quaternion))

    yaw_quaternion = Quaternion.from_z_rotation(math.radians(127))
    yaw_integration_quaternion = body_quaternion.cross(yaw_quaternion)
    compass_quaternion = azimuth_to_quaternion(307)
    if compass_quaternion.dot(yaw_integration_quaternion) < 0.0:
        yaw_integration_quaternion = - yaw_integration_quaternion
    prediction_error = math.degrees(short_angle(compass_quaternion, yaw_integration_quaternion))
    print("Rotation 127°", prediction_error, math.isclose(prediction_error, -15.173506795754871))
    body_quaternion = compass_quaternion.slerp(yaw_integration_quaternion, 0.75)  # 0.75
    print("6 azimuth", quaternion_to_azimuth(compass_quaternion), "slerp", quaternion_to_azimuth(yaw_integration_quaternion), "=", quaternion_to_azimuth(body_quaternion))

    yaw_quaternion = Quaternion.from_z_rotation(math.radians(-30))
    yaw_integration_quaternion = body_quaternion.cross(yaw_quaternion)
    compass_quaternion = azimuth_to_quaternion(334)
    if compass_quaternion.dot(yaw_integration_quaternion) < 0.0:
        yaw_integration_quaternion = - yaw_integration_quaternion
    prediction_error = math.degrees(short_angle(compass_quaternion, yaw_integration_quaternion))
    print("Rotation -30°", prediction_error, math.isclose(prediction_error, -14.384291585315202))
    body_quaternion = compass_quaternion.slerp(yaw_integration_quaternion, 0.75)  # 0.75
    print("7 azimuth", quaternion_to_azimuth(compass_quaternion), "slerp", quaternion_to_azimuth(yaw_integration_quaternion), "=", quaternion_to_azimuth(body_quaternion))

    yaw_quaternion = Quaternion.from_z_rotation(math.radians(79))
    yaw_integration_quaternion = body_quaternion.cross(yaw_quaternion)
    compass_quaternion = azimuth_to_quaternion(234)
    if compass_quaternion.dot(yaw_integration_quaternion) < 0.0:
        yaw_integration_quaternion = - yaw_integration_quaternion
    prediction_error = math.degrees(short_angle(compass_quaternion, yaw_integration_quaternion))
    print("Rotation 79°", prediction_error, math.isclose(prediction_error, -31.791763621723902))
    body_quaternion = compass_quaternion.slerp(yaw_integration_quaternion, 0.75)  # 0.75
    print("8 azimuth", quaternion_to_azimuth(compass_quaternion), "slerp", quaternion_to_azimuth(yaw_integration_quaternion), "=", quaternion_to_azimuth(body_quaternion))

    yaw_quaternion = Quaternion.from_z_rotation(math.radians(-31))
    yaw_integration_quaternion = body_quaternion.cross(yaw_quaternion)
    compass_quaternion = azimuth_to_quaternion(292)
    if compass_quaternion.dot(yaw_integration_quaternion) < 0.0:
        yaw_integration_quaternion = - yaw_integration_quaternion
    prediction_error = math.degrees(short_angle(compass_quaternion, yaw_integration_quaternion))
    print("Rotation -31°", prediction_error, math.isclose(prediction_error, 3.1177579168098366))
    body_quaternion = compass_quaternion.slerp(yaw_integration_quaternion, 0.75)  # 0.75
    print("9 azimuth", quaternion_to_azimuth(compass_quaternion), "slerp", quaternion_to_azimuth(yaw_integration_quaternion), "=", quaternion_to_azimuth(body_quaternion))

    yaw_quaternion = Quaternion.from_z_rotation(math.radians(-16))
    yaw_integration_quaternion = body_quaternion.cross(yaw_quaternion)
    compass_quaternion = azimuth_to_quaternion(311)
    if compass_quaternion.dot(yaw_integration_quaternion) < 0.0:
        yaw_integration_quaternion = - yaw_integration_quaternion
    prediction_error = math.degrees(short_angle(compass_quaternion, yaw_integration_quaternion))
    print("Rotation -16°", prediction_error, math.isclose(prediction_error, 5.3383545006226605))
    body_quaternion = compass_quaternion.slerp(yaw_integration_quaternion, 0.75)  # 0.75
    print("10 azimuth", quaternion_to_azimuth(compass_quaternion), "slerp", quaternion_to_azimuth(yaw_integration_quaternion), "=", quaternion_to_azimuth(body_quaternion))

    yaw_quaternion = Quaternion.from_z_rotation(math.radians(-34))
    yaw_integration_quaternion = body_quaternion.cross(yaw_quaternion)
    compass_quaternion = azimuth_to_quaternion(345)
    if compass_quaternion.dot(yaw_integration_quaternion) < 0.0:
        yaw_integration_quaternion = - yaw_integration_quaternion
    body_direction_delta = math.degrees(short_angle(compass_quaternion, yaw_integration_quaternion))
    print("Rotation -34°", body_direction_delta, math.isclose(body_direction_delta, 4.003946924375679))
    body_quaternion = compass_quaternion.slerp(yaw_integration_quaternion, 0.75)  # 0.75
    print("11 azimuth", quaternion_to_azimuth(compass_quaternion), "slerp", quaternion_to_azimuth(yaw_integration_quaternion), "=", quaternion_to_azimuth(body_quaternion))

    # Test assert_almost_egal_angle
    t = assert_almost_equal_angles(0, math.radians(-176), 90)
    print("Angle -176° and 0° not almost equal", t == False)
