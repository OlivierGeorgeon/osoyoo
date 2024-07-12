# Test PlaceCell geometry
# py -m autocat.Memory.PlaceMemory

import math
import numpy as np
from ...Utils import polar_to_cartesian
from .PlaceGeometry import transform_estimation_cue_to_cue, plot_correspondences, point_to_polar_array, resample_by_diff

polar1 = np.array([[0, -math.pi/4], [10, 0], [10, math.pi/2], [20, 3*math.pi/4]])
cartesian1 = polar_to_cartesian(polar1)
cartesian1 = np.array([[0, 0, 0], [10, 0, 0], [10, 10, 0], [20, 10, 0]])
polar2 = np.array([[0, -math.pi/4], [10, 0], [20, math.pi/2], [20, 3*math.pi/4]])
cartesian2 = polar_to_cartesian(polar2)
cartesian2 = np.array([[0, 0, 0], [10, 0, 0], [10, 10, 0], [20, 12, 0]])

# Test delta echoes
# print("delta echoes", delta_echo_curves(polar1, cartesian1, polar2, cartesian2))

# Test transformation estimation
reg_p2p, _, source_points_transformed = transform_estimation_cue_to_cue(cartesian1, cartesian2, 5)
plot_correspondences(cartesian1, cartesian2, source_points_transformed, np.asarray(reg_p2p.correspondence_set), 0, 0)
print("Transformation\n", reg_p2p.transformation)


# Test point_to_polar_array
print("test point_to_polar_array")
# print(point_to_polar_array(np.array([100, 100, 0])))

print("Streaks")
points = [[1000, 0],
          [1000, 10],
          [1200, 20],
          [1200, 30],
          [1200, 40],
          [1300, 50],
          [1300, 60],
          [1250, 70],
          [1250, 80],
          [1150, 90]
          ]

print("Test resample by diff")
# print(resample_by_diff(points, 20, r_tolerance=10))
