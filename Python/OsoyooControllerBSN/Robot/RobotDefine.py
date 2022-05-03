# Olivier's robot:
#   7V: 160 mm
#   8V: 190 mm
#

# 0: No robot
ROBOT_ID = 4

ROBOT_HEAD_X = 80
ROBOT_FRONT_X = 110
ROBOT_FRONT_Y = 80

STEP_FORWARD_DISTANCE = 120  # Longitudinal translation
SHIFT_DISTANCE = 110         # lateral translation
DEFAULT_YAW = 45             # Default rotation when yaw is not returned by the robot
RETREAT_DISTANCE = 90       # 100 on Robot 3
RETREAT_DISTANCE_Y = 20      # Y displacement when line is detected on the side
LINE_X = 160                 # X coordinate of the line after retreat

# You must set the offset such that compass_x is near 0 when the robot is East or West
#                               and compass_y is near 0 when the robot is North or South.
if ROBOT_ID == 2:
    COMPASS_X_OFFSET = 10
    COMPASS_Y_OFFSET = 60

if ROBOT_ID == 4:
    COMPASS_X_OFFSET = -30  # -28
    COMPASS_Y_OFFSET = -70  #-71
