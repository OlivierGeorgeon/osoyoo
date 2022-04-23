# Olivier's robot:
#   7V: 160 mm
#   8V: 190 mm
#

# 0: No robot
ROBOT_ID = 1

ROBOT_HEAD_X = 80
ROBOT_FRONT_X = 110
ROBOT_FRONT_Y = 80

STEP_FORWARD_DISTANCE = 120  # Longitudinal translation
SHIFT_DISTANCE = 110         # lateral translation
DEFAULT_YAW = 45             # Default rotation when yaw is not returned by the robot
RETREAT_DISTANCE = 90       # 100 on Robot 3
RETREAT_DISTANCE_Y = 20      # Y displacement when line is detected on the side
LINE_X = 160                 # X coordinate of the line after retreat
