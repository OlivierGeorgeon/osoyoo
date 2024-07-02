# Test PlaceCell geometry
# py -m autocat.Memory.PlaceMemory

import math
import numpy as np
from ...Utils import polar_to_cartesian
from .PlaceGeometry import transform_estimation_cue_to_cue, point_to_polar_array, resample_by_diff

polar1 = np.array([[0, -math.pi/4], [10, 0], [10, math.pi/2], [20, 3*math.pi/4]])
cartesian1 = polar_to_cartesian(polar1)
polar2 = np.array([[0, -math.pi/4], [10, 0], [20, math.pi/2], [20, 3*math.pi/4]])
cartesian2 = polar_to_cartesian(polar2)

# Test delta echoes
# print("delta echoes", delta_echo_curves(polar1, cartesian1, polar2, cartesian2))

# Test transformation estimation
transformation = transform_estimation_cue_to_cue(cartesian1, cartesian2)
rotation = transformation[:3, :3]
translation = transformation[:3, 3]
print("Estimated rotation:")
print(rotation)
print("Estimated translation:")
print(translation)

# Test point_to_polar_array
print("test point_to_polar_array")
print(point_to_polar_array(np.array([100, 100, 0])))

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
print(resample_by_diff(points, 10))
