import math
import numpy as np
import pytest
from petitbrain.Utils import polar_to_cartesian
from petitbrain.Memory.PlaceMemory.PlaceGeometry import transform_estimation_cue_to_cue, plot_compare, unscanned_direction, \
    open_direction, point_to_polar_array, resample_by_diff


def test_polar_to_cartesian():
    polar1 = np.array([[0, -math.pi/4], [10, 0], [10, math.pi/2], [20, 3*math.pi/4]])
    cartesian1 = polar_to_cartesian(polar1)
    expected = np.array([[0.00000000e+00, -0.00000000e+00,  0.00000000e+00],
                         [1.00000000e+01,  0.00000000e+00,  0.00000000e+00],
                         [6.12323400e-16,  1.00000000e+01,  0.00000000e+00],
                         [-1.41421356e+01,  1.41421356e+01,  0.00000000e+00]])
    np.testing.assert_allclose(cartesian1, expected), "Wrong points"
    # print("cartesian 1", cartesian1)
    polar2 = np.array([[0, -math.pi/4], [10, 0], [20, math.pi/2], [20, 3*math.pi/4]])
    cartesian2 = polar_to_cartesian(polar2)
    expected2 = np.array([[0.00000000e+00, -0.00000000e+00,  0.00000000e+00],
                          [1.00000000e+01,  0.00000000e+00,  0.00000000e+00],
                          [1.22464680e-15,  2.00000000e+01,  0.00000000e+00],
                          [-1.41421356e+01,  1.41421356e+01,  0.00000000e+00]])
    np.testing.assert_allclose(cartesian2, expected2), "Wrong points"
    # print("cartesian 2", cartesian2)


def test_point_to_polar_array():
    """Test point_to_polar_array"""
    result = point_to_polar_array(np.array([100, 100, 0]))
    # Just test the average of the resulting array
    assert np.mean(result) == pytest.approx(15.713484026367723)


def test_transform_estimate():
    """Test transformation estimation"""
    cartesian1 = np.array([[0, -500, 0], [500, 0, 0], [500, 500, 0], [-500, 500, 0]])
    cartesian2 = np.array([[50, -500, 0], [500, 50, 0], [500, 600, 0], [-500, 600, 0]])
    reg_p2p = transform_estimation_cue_to_cue(cartesian1, cartesian2, 100)
    # print("correspondance set", np.asarray(reg_p2p.correspondence_set))
    expected1 = np.array([[0, 0], [1, 1]])
    expected2 = np.array([[1, 1], [0, 0]])
    assert np.all(np.asarray(reg_p2p.correspondence_set) == expected1) \
           or np.all(np.asarray(reg_p2p.correspondence_set) == expected2)
    # plot_compare(cartesian1, cartesian2, reg_p2p, 0, 0)


@pytest.fixture
def scan_points_fix():
    points = [[1500, 0],
              [1500, 10/180 * math.pi],
              [1200, 20/180 * math.pi],
              [1200, 30/180 * math.pi],
              [1200, 40/180 * math.pi],
              [1300, 50/180 * math.pi],
              [1300, 60/180 * math.pi],
              [1300, 70/180 * math.pi],
              [0, 80/180 * math.pi],
              [1400, 90/180 * math.pi],
              [1400, 100/180 * math.pi],
              [10, 110/180 * math.pi],
              [1500, 120/180 * math.pi],
              [1500, 130/180 * math.pi],
              [1500, 140/180 * math.pi],
              [1500, 150/180 * math.pi],
              [1500, 160/180 * math.pi],
              [1500, 170/180 * math.pi],
              [1500, 180/180 * math.pi]
              ]
    return points


def test_resample_by_diff(scan_points_fix):
    """print("Test resample by diff")"""
    result = resample_by_diff(scan_points_fix, 20, r_tolerance=10)
    expected = np.array([[1.20000000e+03, 3.49065850e-01],
                         [1.20000000e+03, 6.98131701e-01],
                         [1.00000000e+01, 1.91986218e+00]])
    np.testing.assert_allclose(result, expected), "Wrong points"


def test_unscanned_direction(scan_points_fix):
    theta, span = unscanned_direction(scan_points_fix)
    assert round(math.degrees(theta)) == 80, "Should be 80°"
    assert span == 0, "Should be 0"


def test_open_direction(scan_points_fix):
    """Test open_direction"""
    a, min, max = open_direction(scan_points_fix)
    assert a == pytest.approx(-1.3846278732488349), "Should be -1.3846278732488349"
    assert min == pytest.approx(-4.188790204786391), "Should be -4.188790204786391"
    assert max == pytest.approx(1.2217304763960306), "Should be 1.2217304763960306"
