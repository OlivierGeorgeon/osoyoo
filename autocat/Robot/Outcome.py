import json
import math
import numpy as np
import colorsys
from playsound import playsound
from pyrr import Quaternion, Matrix44, matrix44
from .RobotDefine import ROBOT_HEAD_X
from ..Memory.EgocentricMemory.Experience import FLOOR_COLORS
from ..Utils import translation_quaternion_to_matrix


def category_color(color_sensor):
    """Categorize the color from the sensor measure"""
    # https://www.w3.org/wiki/CSS/Properties/color/keywords
    # https://www.colorspire.com/rgb-color-wheel/
    # https://www.pinterest.fr/pin/521713938063708448/
    hsv = colorsys.rgb_to_hsv(float(color_sensor['red']) / 256.0, float(color_sensor['green']) / 256.0,
                              float(color_sensor['blue']) / 256.0)

    if hsv[0] > 0.99 and hsv[1] > 0.4:
        color_index = 1  # red
    elif hsv[0] > 0.986 and color_sensor['blue'] < 55:  # Before calibration 0.98
        color_index = 1  # red
    elif hsv[0] > 0.95:       # Before calibration 0.9
        color_index = 7  # deepPink
    elif hsv[0] > 0.6:      # Hue = 0.83 -- 0.66, sat 0.25
        color_index = 6  # orchid
    elif hsv[0] > 0.5:      # Hue = 0.59 -- 0.57, 0.58 -- 0.58, sat 0.86
        color_index = 5  # deepSkyBlue
    elif hsv[0] > 0.28:     # Hue = 0.38, 0.35, 0.37 -- 0.29, 0.33, 0.29, 0.33 -- 0.36, sat 0.68
        color_index = 4  # limeGreen
    elif hsv[0] > 0.1:      # Before calibration: 0.175:
        color_index = 3  # gold
    elif hsv[0] > 0.02:     # Before calibration: 0.05:
        color_index = 2  # orange
    else:
        color_index = 1  # red

    # Rug at Olivier's
    # Robots see the rug between red and green with low saturation
    if color_index in [1, 2, 3, 4] and hsv[1] < 0.3:
        color_index = 0

    # Floor in UCLy lyon
    # if (hsv[0] < 0.6) and (hsv[1] < 0.3):  # 0.45  // violet (0.66,0.25,0.398) in DOLL
    #     #if hsv[0] < 0.7:  # 0.6
    #         # Not saturate, not violet
    #         # Floor. Saturation: Table bureau 0.16. Sol bureau 0.17, table olivier 0.21, sol olivier: 0.4, 0.33
    #     color_index = 0
        #else:
            # Not saturate but violet
        #    color = 'orchid'  # Hue = 0.75, 0.66 -- 0.66, Saturation = 0.24, 0.34, 0.2 -- 0.2
        #    color_index = 6

    # Yoga mat at DOLL (0.16,0.34,0.42)
    # if hsv[2] < 0.43:
    #     color_index = 0

    # Rug at DOLL
    # if (0.2 < hsv[0] < 0.45) and (hsv[1] < 0.45):
    #     color_index = 0

    # print("Color: ", hsv, FLOOR_COLORS[color_index])
    print("Color:", tuple("{:.3f}".format(x) for x in hsv), FLOOR_COLORS[color_index])
    return color_index


def echo_matrix(head_direction, echo_distance):
    """Return the matrix representing the pose of the echo from direction in degrees and distance"""
    head_quaternion = Quaternion.from_z_rotation(math.radians(head_direction))
    echo_from_head_matrix = translation_quaternion_to_matrix([echo_distance, 0, 0], head_quaternion)
    return Matrix44.from_translation([ROBOT_HEAD_X, 0, 0]) * echo_from_head_matrix


def echo_point(head_direction, echo_distance):
    """Return the egocentric echo point from the head direction and echo distance"""
    return matrix44.apply_to_vector(echo_matrix(head_direction, echo_distance), np.array([0, 0, 0])).astype(int)


def central_echos(echos):
    """Return an array of points representing the centers of streaks of echos"""
    _central_echos = []

    # Create the streaks
    streaks = []
    echo_list = [[int(a), d] for a, d in echos.items()]
    current_streak = [echo_list[0]]
    if len(echo_list) > 1:
        for angle, distance in echo_list[1:]:
            if abs(current_streak[-1][1] - distance) < 50 and abs(angle - current_streak[-1][0]) <= 50:
                current_streak.append([angle, distance])
            else:
                streaks.append(current_streak)
                current_streak = [[angle, distance]]
    streaks.append(current_streak)

    # Find the middle of the streaks
    for streak in streaks:
        if len(streak) == 0:
            continue
        else:
            if len(streak) % 2 == 0:
                # Compute the means of angle and distance values for the two elements at the center of the array
                a_mean = (streak[int(len(streak) / 2)][0] + streak[int(len(streak) / 2) - 1][0]) / 2.
                d_mean = (streak[int(len(streak) / 2)][1] + streak[int(len(streak) / 2) - 1][1]) / 2.
                _central_echos.append([a_mean, d_mean])
            else:
                # The central echo is at the center point of the streak
                _central_echos.append([streak[int(len(streak) / 2)][0], streak[int(len(streak) / 2)][1]])

    # Sort by distance
    _central_echos = sorted(_central_echos, key=lambda e: e[1])
    # Only return the closest central echo
    # if len(_central_echos) > 1:
    #     _central_echos = [_central_echos[0]]
    print("Central echos", _central_echos)

    return _central_echos


class Outcome:
    """The class thant contains the outcome recieved from the robot"""
    def __init__(self, outcome_dict):
        self._dict = outcome_dict  # For print

        # The required unprocessed fields

        self.action_code = outcome_dict['action']
        self.clock = outcome_dict['clock']
        self.duration1 = outcome_dict['duration1']
        self.head_angle = outcome_dict['head_angle']

        # The optional and processed fields

        # The status
        self.status = ""
        if 'status' in outcome_dict:
            self.status = outcome_dict['status']

        # The yaw may not be returned by the robot if it has no imu
        self.yaw = None
        if 'yaw' in outcome_dict:
            self.yaw = outcome_dict['yaw']

        # Floor color
        self.color_index = 0
        if 'color' in outcome_dict:
            self.color_index = category_color(outcome_dict['color'])
        if 'color_index' in outcome_dict:  # Generated by simulated outcome
            self.color_index = outcome_dict['color_index']

        # # Yaw quaternion
        # self.yaw_quaternion = None
        # if 'yaw' in outcome_dict:
        #     self.yaw_quaternion = Quaternion.from_z_rotation(math.radians(outcome_dict['yaw']))

        # Outcome azimuth (not used: we use compass instead)
        self.azimuth = None
        if 'azimuth' in outcome_dict:
            self.azimuth = outcome_dict['azimuth']

        # Outcome compass. Will be adjusted by the offset.
        self.compass_point = None
        # self.compass_quaternion = None  # Is computed by CtrlRobot
        # Also eliminate abnormal values in compass_x or compass_y observed with Robot 2
        if 'compass_x' in outcome_dict:  # and abs(outcome_dict['compass_x']) < 1000 and abs(outcome_dict['compass_y']) < 1000:
            self.compass_point = np.array([outcome_dict['compass_x'], outcome_dict['compass_y'], 0], dtype=int)

        # Outcome floor
        self.floor = 0
        if 'floor' in outcome_dict:
            self.floor = outcome_dict['floor']

        # Outcome echo
        self.echo_point = None
        self.echo_matrix = None
        self.echo_distance = 10000
        if 'echo_distance' in outcome_dict and outcome_dict['echo_distance'] < 10000:
            self.echo_matrix = echo_matrix(outcome_dict['head_angle'], outcome_dict['echo_distance'])
            self.echo_point = matrix44.apply_to_vector(self.echo_matrix, [0, 0, 0])

        # Outcome impact
        # (The Enaction will compute the translation based on duration 1)
        self.impact = 0
        if 'impact' in outcome_dict:
            self.impact = outcome_dict['impact']
            if self.impact > 0:
                playsound('autocat/Assets/cute_beep1.wav', False)

        # Outcome blocked
        # (The Enaction will reset the translation)
        self.blocked = False
        if 'blocked' in outcome_dict:
            self.blocked = outcome_dict['blocked']

        # Outcome echo array for SCAN interactions
        self.echos = {}
        self.central_echos = []
        if "echos" in outcome_dict:
            self.echos = outcome_dict['echos']
            print("Echos", self.echos)
            self.central_echos = central_echos(self.echos)

        # Outcome touch
        self.touch = 0
        if 'touch' in outcome_dict:
            self.touch = outcome_dict['touch']

    def set_clock(self, clock):
        """Set the clock (for predicted_outcome)"""
        self.clock = clock
        self._dict['clock'] = clock

    def __str__(self):
        """Print the outcome as a json string"""
        return json.dumps(self._dict)
