import colorsys
import math
import numpy as np
from pyrr import matrix44
from ...Robot.RobotDefine import ROBOT_HEAD_X

EXPERIENCE_ALIGNED_ECHO = 'Echo'
EXPERIENCE_LOCAL_ECHO = 'Local_Echo'
EXPERIENCE_CENTRAL_ECHO = 'Central_Echo'
EXPERIENCE_BLOCK = 'Block'
EXPERIENCE_IMPACT = 'Shock'
EXPERIENCE_FLOOR = 'Floor'
EXPERIENCE_FOCUS = 'Focus'
EXPERIENCE_PLACE = 'Place'
EXPERIENCE_PROMPT = 'Prompt'
# COLOR_FLOOR = "LightSlateGrey"
FLOOR_COLORS = {0: 'LightSlateGrey', 1: 'red', 2: 'darkOrange', 3: 'gold', 4: 'limeGreen', 5: 'deepSkyBlue',
                6: 'orchid', 7: 'deepPink'}


class Experience:
    """Experiences are instances of interactions
    along with the spatial and temporal information of where and when they were enacted"""

    def __init__(self, x, y, experience_type, body_direction_rad, clock, experience_id, durability=10, color_index=0):
        """Create an experience to be placed in the memory.
        Args:
        x, y : coordinates relative the robot.
        type : type of experience (i.e. Chock, Block, Echolocalisation, Line etc)
        durability : durability of the experience, when it reach zero the experience should be removed from the memory.
        """
        self.point = np.array([x, y, 0])
        self.type = experience_type
        self.absolute_direction_rad = body_direction_rad
        self.clock = clock
        self.id = experience_id
        self.durability = durability
        self.color_index = color_index

        # The position matrix will cumulate the rotation and translations of the robot
        # Used to compute the position of the experience relative to the robot in egocentric memory
        self.position_matrix = matrix44.create_from_translation(self.point).astype('float64')
        # The position of the robot relative to the experience
        # Used to compute the position of the robot relative to the experience
        # opposite_position_matrix = matrix44.create_from_translation(-self.point).astype('float64')
        relative_sensor_point = -self.point  # By default the center of the robot
        # The absolute direction of this experience

        if self.type in [EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_CENTRAL_ECHO]:
            # The position of the echo incorporating the rotation from the head
            head_direction_rad = math.atan2(y, x-ROBOT_HEAD_X)
            self.absolute_direction_rad += head_direction_rad  # The absolute direction of the sensor...
            self.absolute_direction_rad = np.mod(self.absolute_direction_rad, 2*math.pi)  # ...within [0,2pi]
            # print("Absolute direction rad:", round(math.degrees(self.absolute_direction_rad)), "°")
            translation_from_head_matrix = matrix44.create_from_translation([math.sqrt((x-ROBOT_HEAD_X)**2 + y**2),
                                                                             0, 0])
            position_from_head_matrix = matrix44.multiply(translation_from_head_matrix,
                                                          matrix44.create_from_z_rotation(-head_direction_rad))
            # The position matrix initialized with rotation from the head rather than from the center of the robot
            self.position_matrix = matrix44.multiply(position_from_head_matrix,
                                                     matrix44.create_from_translation([ROBOT_HEAD_X, 0, 0])
                                                     .astype('float64'))
            # The position of the head relative to the echo in allocentric coordinates
            # opposite_position_matrix = matrix44.create_from_translation([-x + ROBOT_HEAD_X, -y, 0])
            relative_sensor_point = np.array([-x + ROBOT_HEAD_X, -y, 0])

        # opposite azimuth
        body_direction_matrix = matrix44.create_from_z_rotation(-body_direction_rad)
        # Move the head position by the azimuth
        # sensor_matrix = matrix44.multiply(opposite_position_matrix, body_direction_matrix)
        # self.sensor_point = matrix44.apply_to_vector(sensor_matrix, [0, 0, 0])

        # The allocentric position of the sensor relative to the allocentric position of the experience
        self.sensor_point = matrix44.apply_to_vector(body_direction_matrix, relative_sensor_point)

        # The rotation matrix to display the affordance in phenomenon view
        angle_sensor = math.atan2(self.sensor_point[1], self.sensor_point[0])
        self.rotation_matrix = matrix44.create_from_z_rotation(math.pi - angle_sensor)

    def __str__(self):
        return "(id:" + str(self.id) + ",clock:" + str(self.clock) + ", type:" + self.type + ")"

    def displace(self, displacement_matrix):
        """Displace the experience by the displacement_matrix"""
        # Update the position matrix in robot-centric coordinates
        # by miraculously multiplying the position_matrix by the displacement_matrix
        self.position_matrix = matrix44.multiply(self.position_matrix, displacement_matrix)

        # Recompute the experience's coordinates in robot-centric coordinates
        self.point = matrix44.apply_to_vector(self.position_matrix, [0, 0, 0])

    def save(self):
        """Create a copy of the experience for memory snapshot"""
        saved_experience = Experience(self.point[0], self.point[1], self.type, 0, self.clock, self.id, self.durability,
                                      self.color_index)
        # Clone the position matrix so it can be updated separately
        saved_experience.position_matrix = self.position_matrix.copy()

        # Absolute relative sensor position do not change
        saved_experience.absolute_direction_rad = self.absolute_direction_rad
        # saved_experience.sensor_matrix = self.sensor_matrix
        saved_experience.rotation_matrix = self.rotation_matrix
        return saved_experience


def category_color(color_sensor):
    """Categorize the color from the sensor measure"""
    # https://www.w3.org/wiki/CSS/Properties/color/keywords
    # https://www.colorspire.com/rgb-color-wheel/
    # https://www.pinterest.fr/pin/521713938063708448/
    hsv = colorsys.rgb_to_hsv(float(color_sensor['red']) / 256.0, float(color_sensor['green']) / 256.0,
                              float(color_sensor['blue']) / 256.0)

    if hsv[1] < 0.45:
        if hsv[0] < 0.6:
            # Not saturate, not violet
            # Floor. Saturation: Table bureau 0.16. Sol bureau 0.17, table olivier 0.21, sol olivier: 0.4, 0.33
            color_index = 0
        else:
            # Not saturate but violet
            color = 'orchid'  # Hue = 0.66 -- 0.66, Saturation = 0.34, 0.2 -- 0.2
            color_index = 6
    else:
        # 'red'  # Hue = 0 -- 0.0, 0.0, sat 0.59
        color_index = 1
        if hsv[0] < 0.98:
            if hsv[0] > 0.9:
                # 'deepPink'  # Hue = 0.94, 0.94, 0.94, 0.96, 0.95, sat 0.54
                color_index = 7
            elif hsv[0] > 0.6:
                # 'orchid'  # Hue = 0.66
                color_index = 6
            elif hsv[0] > 0.5:
                # 'deepSkyBlue'  # Hue = 0.59 -- 0.57, 0.58 -- 0.58, sat 0.86
                color_index = 5
            elif hsv[0] > 0.28:
                # 'limeGreen'  # Hue = 0.38, 0.35, 0.37 -- 0.29, 0.33, 0.29, 0.33 -- 0.36, sat 0.68
                color_index = 4
            elif hsv[0] > 0.175:
                # 'gold'  # Hue = 0.25, 0.26 -- 0.20 -- 0.20, 0.20, 0.184, 0.2 -- 0.24, sat 0.68
                color_index = 3
            elif hsv[0] > 0.05:
                # 'darkOrange'  # Hue = 0.13, 0.16, 0.15 -- 0.06, 0.08, 0.09, 0.08 -- 0.11, sat 0.56
                color_index = 2

    # print("Color: ", hsv, FLOOR_COLORS[color_index])
    return color_index
