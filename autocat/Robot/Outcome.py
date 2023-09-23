# import json
import math
import numpy as np
import colorsys
from playsound import playsound
from pyrr import Quaternion
from .RobotDefine import RETREAT_DISTANCE, RETREAT_DISTANCE_Y, ROBOT_HEAD_X
from ..Memory.EgocentricMemory.Experience import FLOOR_COLORS


def category_color(color_sensor):
    """Categorize the color from the sensor measure"""
    # https://www.w3.org/wiki/CSS/Properties/color/keywords
    # https://www.colorspire.com/rgb-color-wheel/
    # https://www.pinterest.fr/pin/521713938063708448/
    hsv = colorsys.rgb_to_hsv(float(color_sensor['red']) / 256.0, float(color_sensor['green']) / 256.0,
                              float(color_sensor['blue']) / 256.0)

    # 'red'  # Hue = 0 -- 0.0, 0.0, sat 0.59
    color_index = 1
    if hsv[0] < 0.98:
        if hsv[0] > 0.9:
            # 'deepPink'  # Hue = 0.94, 0.94, 0.94, 0.96, 0.95, sat 0.54
            color_index = 7
        elif hsv[0] > 0.6:  # 0.7  # 0.6
            # 'orchid'  # Hue = 0.83 -- 0.66, sat 0.25
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
            # 'orange'
            color_index = 2

    # Rug at Olivier's
    if color_index in [3, 4] and hsv[1] < 0.6 and hsv[2] < 0.5:
        color_index = 0

    # Floor in UCLy lyon
    if (hsv[0] < 0.6) and (hsv[1] < 0.3):  # 0.45  // violet (0.66,0.25,0.398) in DOLL
        #if hsv[0] < 0.7:  # 0.6
            # Not saturate, not violet
            # Floor. Saturation: Table bureau 0.16. Sol bureau 0.17, table olivier 0.21, sol olivier: 0.4, 0.33
        color_index = 0
        #else:
            # Not saturate but violet
        #    color = 'orchid'  # Hue = 0.75, 0.66 -- 0.66, Saturation = 0.24, 0.34, 0.2 -- 0.2
        #    color_index = 6

    # Yoga mat at DOLL (0.16,0.34,0.42)
    # if hsv[2] < 0.43:
    #     color_index = 0

    # Rug at DOLL
    if (0.2 < hsv[0] < 0.45) and (hsv[1] < 0.45):
        color_index = 0

    # print("Color: ", hsv, FLOOR_COLORS[color_index])
    print("Color:", tuple("{:.3f}".format(x) for x in hsv), FLOOR_COLORS[color_index])
    return color_index


def central_echos(echos):
    """Return an array of points representing the centers of streaks of echos"""

    _central_echos = []
    # max_delta_dist = 160
    # max_delta_angle = 20
    streaks = []  # [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    current_id = 0
    # echos = {int(a): d for a, d in sorted(echos.items(), key=lambda item: int(item[0]))}
    echo_list = [[int(a), d] for a, d in echos.items()]
    # print("Sorted echos", echos)
    # Create the streaks
    current_streak = [echo_list[0]]
    if len(echo_list) > 1:
        for angle, distance in echo_list[1:]:
            # if len(current_streak) == 0:
            #     current_streak.append([angle, distance])
            if abs(current_streak[-1][1] - distance) < 50 and abs(angle - current_streak[-1][0]) <= 10:
                current_streak.append([angle, distance])
            else:
                streaks.append(current_streak)
                current_streak = [[angle, distance]]
    streaks.append(current_streak)

    # for angle, distance in echo_list:
    #     check = False
    #     for streak in streaks:
    #         if len(streak) > 0 and not check and \
    #            any((abs(e[1] - distance) < max_delta_dist and abs(angle - e[0]) < max_delta_angle) for e in streak):
    #             streak.append((angle, distance))
    #             check = True
    #     if check:
    #         continue
    #     if len(streaks[current_id]) == 0:
    #         streaks[current_id].append((angle, distance))
    #     else:
    #         current_id = (current_id + 1)
    #         streaks[current_id].append((angle, distance))
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
    # print("Central echos", _central_echos)
    return _central_echos


class Outcome:
    """The class thant contains the outcome recieved from the robot"""
    def __init__(self, outcome_dict):

        # outcome_dict = json.loads(outcome_string)
        self.action_code = outcome_dict['action']
        self.clock = outcome_dict['clock']
        self.duration1 = outcome_dict['duration1']
        self.status = outcome_dict['status']
        self.head_angle = outcome_dict['head_angle']
        self.retreat_translation = np.array([0, 0, 0], dtype=int)

        # Floor color
        self.color_index = 0
        if 'color' in outcome_dict:
            self.color_index = category_color(outcome_dict['color'])

        # Outcome yaw
        self.yaw_quaternion = None
        if 'yaw' in outcome_dict:
            self.yaw_quaternion = Quaternion.from_z_rotation(math.radians(outcome_dict['yaw']))

        # Outcome azimuth (not used: we use compass instead)
        self.azimuth = None
        if 'azimuth' in outcome_dict:
            self.azimuth = outcome_dict['azimuth']

        # Outcome compass. Will be adjusted by the offset.
        self.compass_point = None
        self.compass_quaternion = None  # Is computed by CtrlRobot
        if 'compass_x' in outcome_dict:
            self.compass_point = np.array([outcome_dict['compass_x'], outcome_dict['compass_y'], 0], dtype=int)

        # Outcome floor
        self.floor = 0
        self.retreat_translation = np.array([0, 0, 0], dtype=int)
        if 'floor' in outcome_dict:
            self.floor = outcome_dict['floor']
            if outcome_dict['floor'] > 0:
                # Update the translation
                if outcome_dict['floor'] == 0b01:
                    # Black line on the right
                    self.retreat_translation = [-RETREAT_DISTANCE, RETREAT_DISTANCE_Y, 0]
                elif outcome_dict['floor'] == 0b10:
                    # Black line on the left
                    self.retreat_translation = [-RETREAT_DISTANCE, -RETREAT_DISTANCE_Y, 0]
                else:
                    # Black line on the front
                    self.retreat_translation = [-RETREAT_DISTANCE, 0, 0]
                # playsound('autocat/Assets/tiny_beep.wav', False)
                playsound('autocat/Assets/cyberpunk3.wav', False)

        # Outcome echo
        self.echo_point = None
        if outcome_dict['echo_distance'] < 10000:
            x = ROBOT_HEAD_X + math.cos(math.radians(outcome_dict['head_angle'])) * outcome_dict['echo_distance']
            y = math.sin(math.radians(outcome_dict['head_angle'])) * outcome_dict['echo_distance']
            self.echo_point = np.array([x, y, 0], dtype=int)

        # Outcome impact
        # (The Enaction will compute the translation based on duration 1)
        self.impact = 0
        if 'impact' in outcome_dict:
            self.impact = outcome_dict['impact']
            if self.impact > 0:
                playsound('autocat/Assets/cute_beep1.wav', False)

        # Interaction blocked
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
