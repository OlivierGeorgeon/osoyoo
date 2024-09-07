import numpy as np

MIN_PLACE_CELL_DISTANCE = 200  # 100
ICP_DISTANCE_THRESHOLD = 100  # 300
ICP_MIN_POINTS = 3  # Minimum number of matching points to compute the position correction
ICP_MAX_ROTATION = 10  # Degree max rotation to compute the position correction
ANGULAR_RESOLUTION = 1  # Degree
CONE_HALF_ANGLE = 20  # 25

# Arrays to compute the echo curve
MASK_ARRAY = np.zeros(360 // ANGULAR_RESOLUTION, dtype=float)
MASK_ARRAY[:CONE_HALF_ANGLE // ANGULAR_RESOLUTION] = 1
MASK_ARRAY[-CONE_HALF_ANGLE // ANGULAR_RESOLUTION:] = 1
