# Olivier's robot:
#   7V: 160 mm
#   8V: 190 mm
#

# 0: No robot
ROBOT_ID = 4  # 1: UCLy's robot. 2: Titouan and Olivier's robot, 4: SHS's robot

ROBOT_HEAD_X = 80           # (mm) The X position of the head pivot
ROBOT_FRONT_X = 110         # (mm) The X position of the robot front
ROBOT_FRONT_Y = 80          # (mm) The Y position of the robot front to mark lateral shocks

FORWARD_SPEED = 180         # (mm/s) Forward translation speed. previous 120.
LATERAL_SPEED = 110         # (mm/s) Lateral translation speed
DEFAULT_YAW = 45            # (degree) Default rotation when yaw is not returned by the robot
RETREAT_DISTANCE = 90       # (mm) Distance travelled during retreat
RETREAT_DISTANCE_Y = 20     # (mm) Y displacement when line is detected on the side
LINE_X = 160                # (mm) X coordinate of the line after retreat

# You must set the compass offset to the center of the circle drawn by the (compass_x, compass_y) points.
# Display the compass points of interest in Egocentric view.
# See screenshot docs/first_steps/compass_calibration.png
# See https://www.best-microcontroller-projects.com/hmc5883l.html
# compass_x must be near 0 when the robot is East or West
# compass_y must be near 0 when the robot is North or South.

if ROBOT_ID == 1:
    FORWARD_SPEED = 300  # (mm/s) Forward translation speed.
    LATERAL_SPEED = 260  # (mm/s) Lateral translation speed.

# Robot 2 in ROOM A327.
if ROBOT_ID == 2:
    COMPASS_X_OFFSET = 0  # The offset is configured in the C++ code.
    COMPASS_Y_OFFSET = 0
    FORWARD_SPEED = 230  # (mm/s) Forward translation speed.
    LATERAL_SPEED = 140  # (mm/s) Lateral translation speed.

# Robot 4 chezOlivier
if ROBOT_ID == 4:
    COMPASS_X_OFFSET = 0
    COMPASS_Y_OFFSET = 0
    FORWARD_SPEED = 120     # (mm/s) Forward translation speed.
    RETREAT_DISTANCE = 70   # (mm) Distance of the line after retreat


SCAN_DISTANCE = 800
