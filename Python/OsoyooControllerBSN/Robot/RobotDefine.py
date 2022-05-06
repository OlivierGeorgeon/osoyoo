# Olivier's robot:
#   7V: 160 mm
#   8V: 190 mm
#

# 0: No robot
ROBOT_ID = 2

ROBOT_HEAD_X = 80
ROBOT_FRONT_X = 110
ROBOT_FRONT_Y = 80

STEP_FORWARD_DISTANCE = 120  # Longitudinal translation
SHIFT_DISTANCE = 110         # lateral translation
DEFAULT_YAW = 45             # Default rotation when yaw is not returned by the robot
RETREAT_DISTANCE = 90       # 100 on Robot 3
RETREAT_DISTANCE_Y = 20      # Y displacement when line is detected on the side
LINE_X = 160                 # X coordinate of the line after retreat

# You must set the compass offset to the center of the circle drawn by the (compass_x, compass_y) points.
# Display the compass points of interest in Egocentric memory.
# See screenshot docs/first_steps/compass_calibration.png
# compass_x must be near 0 when the robot is East or West
# compass_y must be near 0 when the robot is North or South.

if ROBOT_ID == 2:
    COMPASS_X_OFFSET = 0  # Robot 2 in ROOM A327.
    COMPASS_Y_OFFSET = 0  # The offset is configured in the C++ code.

if ROBOT_ID == 4:
    COMPASS_X_OFFSET = -50  # Robot 4 chezOlivier
    COMPASS_Y_OFFSET = -120
