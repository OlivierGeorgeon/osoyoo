# Olivier's robot:
#   7V: 160 mm
#   8V: 190 mm
#

ROBOT_HEAD_X = 80           # (mm) The X position of the head pivot
ROBOT_FRONT_X = 110         # (mm) The X position of the robot front
ROBOT_FRONT_Y = 80          # (mm) The Y position of the robot front to mark lateral shocks
ROBOT_SIDE = 120            # (mm) The Y position of the outside border of the robot
ROBOT_COLOR_X = 50          # (mm) The X position of the color sensor

DEFAULT_YAW = 45            # (degree) Default rotation when yaw is not returned by the robot
TURN_DURATION = 1.000       # (s) The duration of turn left and turn right actions
TRANSLATE_DURATION = 1.     # (s) The duration of longitudinal or lateral translation
RETREAT_DISTANCE = 80  # 90       # (mm) Distance travelled during retreat
RETREAT_DISTANCE_Y = 20  # 75     # (mm) Y displacement when line is detected on the side
LINE_X = 150  # 160              # (mm) X coordinate of the line after retreat

SCAN_DISTANCE = 800

TERRAIN_RADIUS = {"A328": [200, 950, 0],     # 1010mm
                  # "A328": [713, 713, 0],    # 1010mm azimuth  45
                  # "A328": [-579, 827, 0],   # 1010mm azimuth  325
                  "A301": [770, 920, 0],      # 1200mm azimuth 40°
                  "PetiteIA": [536, 450, 0],  # 700mm azimuth 50°
                  "DOLL": [770, 920, 0]}      # To be defined

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
ROBOT_SETTINGS_1["compass_offset"] = [67, -42, 0] # [0, 0, 0]  # Compass offset can also be added into the C++ code.

# Robot 2 in Lyon.
ROBOT_SETTINGS_2 = ROBOT_SETTINGS_0.copy()
ROBOT_SETTINGS_2["IP"] = {"A328": "192.168.8.189", "PetiteIA": "192.168.8.189"}
ROBOT_SETTINGS_2["forward_speed"] = 230  # (mm/s) Forward translation speed.
ROBOT_SETTINGS_2["lateral_speed"] = 140  # (mm/s) Lateral translation speed.
ROBOT_SETTINGS_2["retreat_distance"] = 90
ROBOT_SETTINGS_2["compass_offset"] = [0, -40, 0]  # [-30, 40, 0]

# Robot 3 chez Olivier
ROBOT_SETTINGS_3 = ROBOT_SETTINGS_0.copy()
ROBOT_SETTINGS_3["IP"] = {"A301": "192.168.8.242", "PetiteIA": "192.168.8.108"}  # 242
# Lower speed cause the robot to believe the arena is smaller. Reduce speed to prevent pushing outside objects
ROBOT_SETTINGS_3["forward_speed"] = 250  # 260  # 230  190 (mm/s) Forward translation speed.
ROBOT_SETTINGS_3["lateral_speed"] = 170  # 230  160  # (mm/s) Lateral translation speed.
ROBOT_SETTINGS_3["retreat_distance"] = 80  # 70   # (mm) Distance of the line after retreat
ROBOT_SETTINGS_3["compass_offset"] = [0, 0, 0]  # [-50, 0, 0] [50, -50, 0]  # [30, -20, 0]  # [-40, 7, 0]  # [-30, 40, 0]

# Robot 4 chez Olivier
ROBOT_SETTINGS_4 = ROBOT_SETTINGS_0.copy()
ROBOT_SETTINGS_4["IP"] = {"PetiteIA": "192.168.8.242"}  # 108
ROBOT_SETTINGS_4["forward_speed"] = 320  # 250
ROBOT_SETTINGS_4["lateral_speed"] = 250
ROBOT_SETTINGS_4["retreat_distance"] = 80  # 120  # 80
ROBOT_SETTINGS_4["compass_offset"] = [40, -10, 0]

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
