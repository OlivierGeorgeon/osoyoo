import json
import math
import numpy as np
from pyrr import Quaternion, matrix44
from ..Decider.Action import ACTION_FORWARD, ACTION_BACKWARD, ACTION_SWIPE, ACTION_RIGHTWARD, \
    ACTION_TURN, ACTION_TURN_HEAD, ACTION_WATCH, ACTION_SCAN
from .RobotDefine import DEFAULT_YAW

ENACTION_DEFAULT_TIMEOUT = 6  # Seconds
DIRECTION_FRONT = 0  # Direction code to go to turn to the prompt
DIRECTION_BACK = 1
DIRECTION_LEFT = 2
DIRECTION_RIGHT = 3


class Command:
    """A command to send to the robot"""
    def __init__(self, action, prompt_point, focus_point, direction, span, color, caution):
        self.action = action
        self.duration = None
        self.angle = None
        self.focus_x = None
        self.focus_y = None
        self.speed = None
        self.caution = None  # 1  # Check for obstacles when moving forward
        self.span = None
        self.color = color
        self.caution = None

        # Compute the duration and angle
        if prompt_point is not None:
            if self.action.action_code in [ACTION_FORWARD, ACTION_BACKWARD]:
                self.duration = int(math.fabs(prompt_point[0] / self.action.translation_speed[0] * 1000))
            if self.action.action_code in [ACTION_SWIPE]:
                self.duration = int(math.fabs(prompt_point[1] / self.action.translation_speed[1] * 1000))
                if prompt_point[1] < 0:
                    self.speed = -int(self.action.translation_speed[1])  # Negative speed makes swipe right
            if self.action.action_code in [ACTION_TURN_HEAD, ACTION_TURN]:
                if direction == DIRECTION_BACK:
                    # Turn the back to the prompt
                    self.angle = int(math.degrees(-math.atan2(prompt_point[1], -prompt_point[0])))
                elif direction == DIRECTION_LEFT:
                    # Turn the the left side to the prompt (-90°)
                    self.angle = int(math.degrees(math.atan2(-prompt_point[0], prompt_point[1])))
                elif direction == DIRECTION_RIGHT:
                    # Turn the the right side to the prompt (+90°)
                    self.angle = int(math.degrees(math.atan2(prompt_point[0], -prompt_point[1])))
                else:
                    # Turn the front to the prompt
                    self.angle = int(math.degrees(math.atan2(prompt_point[1], prompt_point[0])))
        else:
            # Default backward 0.5s
            if self.action.action_code in [ACTION_BACKWARD]:
                self.duration = 500
            # Default sidewards 1.5s
            if self.action.action_code in [ACTION_SWIPE, ACTION_RIGHTWARD]:
                self.duration = 1000  # 1500
        if self.action.action_code in [ACTION_WATCH]:
            self.duration = 1000  # 5000

        # Compute the focus
        if focus_point is not None:
            self.focus_x = int(focus_point[0])  # Convert to python int
            self.focus_y = int(focus_point[1])
            if self.action.action_code == ACTION_FORWARD:
                self.speed = int(self.action.translation_speed[0])
            if self.action.action_code == ACTION_BACKWARD:
                self.speed = -int(self.action.translation_speed[0])
            if self.action.action_code in [ACTION_SWIPE, ACTION_RIGHTWARD]:
                self.speed = int(self.action.translation_speed[1])
                if prompt_point is not None:
                    self.speed = math.copysign(int(self.action.translation_speed[1]), prompt_point[1])

        # The additional fields of the command packet
        if caution > 0:
            self.caution = caution  # 1: stop if there is an obstacle on the way

        if span != 40 and self.action.action_code == ACTION_SCAN:
            self.span = span

        # The anticipated displacement
        if self.duration is None:
            if self.speed is None or self.speed > 0 or self.action.action_code in [ACTION_RIGHTWARD]:
                self.predicted_translation = action.translation_speed * action.target_duration
            else:
                self.predicted_translation = - action.translation_speed * action.target_duration
        else:
            if self.speed is None or self.speed > 0 or self.action.action_code in [ACTION_RIGHTWARD]:
                self.predicted_translation = action.translation_speed * self.duration / 1000
            else:
                self.predicted_translation = - action.translation_speed * self.duration / 1000

        # The anticipated yaw quaternion
        if self.angle is None:
            self.predicted_yaw_quaternion = Quaternion.from_z_rotation(action.rotation_speed_rad * action.target_duration)
        else:
            self.predicted_yaw_quaternion = Quaternion.from_z_rotation(math.radians(self.angle))

        # The displacement matrix of the environment relative to the robot
        self.predicted_yaw_matrix = matrix44.create_from_quaternion(self.predicted_yaw_quaternion)
        self.predicted_displacement_matrix = matrix44.multiply(
            matrix44.create_from_translation(-self.predicted_translation), self.predicted_yaw_matrix)

    def command_dict(self):
        """Return a dictionary containing the command"""
        # The clock is not included because it is allocated during the enaction
        command_dict = {'action': self.action.action_code}
        if self.duration is not None:
            command_dict['duration'] = self.duration
        if self.angle is not None:
            command_dict['angle'] = self.angle
        if self.focus_x is not None:
            command_dict['focus_x'] = self.focus_x
            command_dict['focus_y'] = self.focus_y
        if self.speed is not None:
            command_dict['speed'] = int(self.speed)
        if self.caution is not None:
            command_dict['caution'] = self.caution
        if self.span is not None:
            command_dict['span'] = self.span
        if self.color is not None:
            command_dict['color'] = self.color
        return command_dict

    def timeout(self):
        """Return the timeout expected from this command"""
        timeout = ENACTION_DEFAULT_TIMEOUT
        if self.duration is not None:
            timeout = self.duration / 1000.0 + 4.0
        if self.angle is not None:
            timeout = math.fabs(self.angle) / DEFAULT_YAW + 4.0  # Turn speed = 45°/s
        return timeout
