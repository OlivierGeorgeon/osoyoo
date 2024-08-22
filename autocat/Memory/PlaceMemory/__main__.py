# Test PlaceCell geometry
# py -m autocat.Memory.PlaceMemory

import math
import numpy as np
from ...Utils import polar_to_cartesian
from .PlaceGeometry import transform_estimation_cue_to_cue, plot_compare, unscanned_direction, open_direction, \
    open_direction, point_to_polar_array, resample_by_diff

polar1 = np.array([[0, -math.pi/4], [10, 0], [10, math.pi/2], [20, 3*math.pi/4]])
cartesian1 = polar_to_cartesian(polar1)
cartesian1 = np.array([[0, -500, 0], [500, 0, 0], [500, 500, 0], [-500, 500, 0]])
polar2 = np.array([[0, -math.pi/4], [10, 0], [20, math.pi/2], [20, 3*math.pi/4]])
cartesian2 = polar_to_cartesian(polar2)
cartesian2 = np.array([[50, -500, 0], [500, 50, 0], [500, 600, 0], [-500, 600, 0]])

# Test delta echoes
# print("delta echoes", delta_echo_curves(polar1, cartesian1, polar2, cartesian2))

# Test transformation estimation
reg_p2p = transform_estimation_cue_to_cue(cartesian1, cartesian2, 5)
# plot_compare(cartesian1, cartesian2, reg_p2p, 0, 0)
print("Transformation\n", reg_p2p.transformation)


# Test point_to_polar_array
print("test point_to_polar_array")
# print(point_to_polar_array(np.array([100, 100, 0])))

print("Streaks")
math.pi/180
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
          [1500, 120/180 * math.pi]
          ]

# print("Test resample by diff")
# print(resample_by_diff(points, 20, r_tolerance=10))

# theta, span = unscanned_direction(points)
# print(f"Direction unscanned {round(math.degrees(theta))}°, span {round(math.degrees(span))}")

# print(f"Open direction {round(math.degrees(open_direction(points)))}°")

print("Open direction > 500")
a, min, max = open_direction(points)
print(f"Open_direction: average: {a}, min: {min}, max: {max}")
