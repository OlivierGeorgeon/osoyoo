import numpy as np
from pyrr import Vector3
from ..Utils import azimuth_to_quaternion


# Olivier's robot:
#   7V: 160 mm
#   8V: 190 mm
#

CHECK_OUTSIDE = 0           # 1 if robot checks echos outside terrain

ROBOT_COLOR_SENSOR_X = 50   # (mm) The X position of the color sensor
ROBOT_HEAD_X = 80           # (mm) The X position of the head pivot
ROBOT_CHASSIS_X = 100       # (mm) The X position of the robot front chassis
ROBOT_FLOOR_SENSOR_X = 110  # (mm) The X position of the robot floor sensor
ROBOT_CHASSIS_Y = 80        # (mm) The Y position of the robot front to mark lateral shocks
ROBOT_OUTSIDE_Y = 120       # (mm) The Y position of the outside border of the robot

DEFAULT_YAW = 45            # (degree) Default rotation when yaw is not returned by the robot
TURN_DURATION = 1.000       # (s) The duration of turn left and turn right actions
TRANSLATE_DURATION = 1.     # (s) The duration of longitudinal or lateral translation
# RETREAT_DISTANCE = 90  # 150  # 90       # (mm) Distance travelled during retreat.
RETREAT_DISTANCE_Y = 20  # 75     # (mm) Y displacement when line is detected on the side
LINE_X = 150  # 160              # (mm) X coordinate of the line after retreat

# SCAN_DISTANCE = 800

TERRAIN_RADIUS = {"A328": {"radius": 1100, "azimuth": 25, "short_radius": 800},  #  25 990 x 600  45},
                  # "PetiteIA": {"radius": 600, "azimuth": 50},  # Petit tapis
                  "PetiteIA": {"radius": 1100, "azimuth": 55, "short_radius": 650},  # {990, 60},  # Grand tapis
                  "A301": {"radius": 1200, "azimuth": 50},
                  "DOLL": {"radius": 1200, "azimuth": 0, "short_radius": 1000}      # To be defined
}

# You must set the compass offset to the center of the circle drawn by the (compass_x, compass_y) points.
# Display the compass points of interest in Egocentric view.
# See screenshot docs/first_steps/compass_calibration.png
# See https://www.best-microcontroller-projects.com/hmc5883l.html
# compass_x must be near 0 when the robot is East or West
# compass_y must be near 0 when the robot is North or South.

ROBOT_SETTINGS_0 = {
    "forward_speed": 300,  # (mm/s) Forward translation speed.
    "lateral_speed": 140,  # (mm/s) Lateral translation speed.
    "retreat_distance": 80,  # 70   # (mm) Distance of the line after retreat
    "compass_offset": [0, 0, 0]  # Compass offset can also be added into the C++ code.
    }

# Robot 1 in Lyon.
ROBOT_SETTINGS_1 = ROBOT_SETTINGS_0.copy()
ROBOT_SETTINGS_1["IP"] = {"A328": "192.168.8.230", "PetiteIA": "192.168.8.0"}
ROBOT_SETTINGS_1["forward_speed"] = 300  # (mm/s) Forward translation speed.
ROBOT_SETTINGS_1["lateral_speed"] = 260  # (mm/s) Lateral translation speed.
ROBOT_SETTINGS_1["retreat_distance"] = 90  # 70   # (mm) Distance of the line after retreat
ROBOT_SETTINGS_1["compass_offset"] = [57, 21, 0]  # [0, 0, 0]  # Compass offset can also be added into the C++ code.

# Robot 2 in Lyon.
ROBOT_SETTINGS_2 = ROBOT_SETTINGS_0.copy()
ROBOT_SETTINGS_2["IP"] = {"A328": "192.168.8.189", "PetiteIA": "192.168.8.189"}
ROBOT_SETTINGS_2["forward_speed"] = 230  # (mm/s) Forward translation speed.
ROBOT_SETTINGS_2["lateral_speed"] = 140  # (mm/s) Lateral translation speed.
ROBOT_SETTINGS_2["retreat_distance"] = 90
ROBOT_SETTINGS_2["compass_offset"] = [0, 0, 0]  # [-30, 40, 0]

# Robot 3 chez Olivier
ROBOT_SETTINGS_3 = ROBOT_SETTINGS_0.copy()
ROBOT_SETTINGS_3["IP"] = {"A301": "192.168.8.242", "PetiteIA": "192.168.8.108"}  # 242
# Lower speed cause the robot to believe the arena is smaller. Reduce speed to prevent pushing outside objects
ROBOT_SETTINGS_3["forward_speed"] = 190  # 260  # 230  190 (mm/s) Forward translation speed.
ROBOT_SETTINGS_3["lateral_speed"] = 130  # 170  # 230  160  # (mm/s) Lateral translation speed.
ROBOT_SETTINGS_3["retreat_distance"] = 90  # 70   # (mm) Distance of the line after retreat
ROBOT_SETTINGS_3["compass_offset"] = [0, 0, 0]  # [-50, 0, 0] [50, -50, 0]  # [30, -20, 0]  # [-40, 7, 0]  # [-30, 40, 0]

# Robot 4 chez Olivier
ROBOT_SETTINGS_4 = ROBOT_SETTINGS_0.copy()
ROBOT_SETTINGS_4["IP"] = {"PetiteIA": "192.168.8.242"}  # 108
ROBOT_SETTINGS_4["forward_speed"] = 330  # 320
ROBOT_SETTINGS_4["lateral_speed"] = 200  # 50
ROBOT_SETTINGS_4["retreat_distance"] = 150  # Increase it if the line keeps being pushed farther
ROBOT_SETTINGS_4["compass_offset"] = [0, 0, 0]  # [33, -5, 0]  # [50, -5, 0]  # [76, 0, 0]

# Robot 1 at DOLL
ROBOT_SETTINGS_11 = ROBOT_SETTINGS_0.copy()
ROBOT_SETTINGS_11["IP"] = {"DOLL": "192.168.11.161"}
ROBOT_SETTINGS_11["forward_speed"] = 290
ROBOT_SETTINGS_11["compass_offset"] = [0, 0, 0]

# Robot 2 at DOLL
ROBOT_SETTINGS_12 = ROBOT_SETTINGS_0.copy()
ROBOT_SETTINGS_12["IP"] = {"DOLL": "192.168.11.174"}
ROBOT_SETTINGS_12["forward_speed"] = 260

# Robot 3 at DOLL
ROBOT_SETTINGS_13 = ROBOT_SETTINGS_0.copy()
ROBOT_SETTINGS_13["IP"] = {"DOLL": "192.168.11.197"}
ROBOT_SETTINGS_13["forward_speed"] = 290

# Robot 4 at DOLL
ROBOT_SETTINGS_14 = ROBOT_SETTINGS_0.copy()
ROBOT_SETTINGS_14["IP"] = {"DOLL": "192.168.11.184"}
ROBOT_SETTINGS_14["forward_speed"] = 210

ROBOT_SETTINGS = {
    '1': ROBOT_SETTINGS_1,
    '2': ROBOT_SETTINGS_2,
    '3': ROBOT_SETTINGS_3,
    '4': ROBOT_SETTINGS_4,
    '11': ROBOT_SETTINGS_11,
    '12': ROBOT_SETTINGS_12,
    '13': ROBOT_SETTINGS_13,
    '14': ROBOT_SETTINGS_14,
    }


def terrain_quaternion(arena_id):
    """Return the quaternion representing the terrain orientation from center to NE"""
    return azimuth_to_quaternion(TERRAIN_RADIUS[arena_id]["azimuth"])


def terrain_north_east_point(arena_id):
    """Return the point of the color patch in polar egocentric relative to the terrain center"""
    return np.array(terrain_quaternion(arena_id) * Vector3([TERRAIN_RADIUS[arena_id]["radius"], 0, 0]), dtype=int)

