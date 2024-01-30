import json
import math
from pyrr import Quaternion, matrix44
from ..Decider.Action import ACTION_FORWARD, ACTION_BACKWARD, ACTION_SWIPE, ACTION_RIGHTWARD, ACTION_TURN, \
    ACTION_TURN_HEAD
from .RobotDefine import DEFAULT_YAW, DEFAULT_ACTION_DURATION

ENACTION_DEFAULT_TIMEOUT = 6  # Seconds
DIRECTION_FRONT = 0  # Direction code to go to turn to the prompt
DIRECTION_BACK = 1
DIRECTION_LEFT = 2
DIRECTION_RIGHT = 3


class Command:
    """A command to send to the robot"""
    def __init__(self, action, prompt_point, focus_point, direction, span, color, caution):

        # The required fields
        self.action = action
        self.duration = action.target_duration * 1000  # Default duration
        self.angle = round(math.degrees(action.rotation_speed_rad * action.target_duration))
        self.speed_x = self.action.translation_speed[0]
        self.speed_y = self.action.translation_speed[1]
        self.color = color
        self.caution = caution
        self.span = span

        # The focus fields are optional
        self.focus_x = None
        self.focus_y = None

        # Override the default duration and angle on the basis of the prompt
        if prompt_point is not None:
            if self.action.action_code in [ACTION_FORWARD, ACTION_BACKWARD]:
                self.duration = int(math.fabs(prompt_point[0] / self.action.translation_speed[0] * 1000))
            if self.action.action_code in [ACTION_SWIPE]:
                self.duration = int(math.fabs(prompt_point[1] / self.action.translation_speed[1] * 1000))
                if prompt_point[1] < 0:
                    self.speed_y = -int(self.action.translation_speed[1])  # Negative speed makes swipe right
            if self.action.action_code in [ACTION_TURN_HEAD, ACTION_TURN]:
                if direction == DIRECTION_BACK:
                    # Turn the back to the prompt
                    angle = -math.atan2(prompt_point[1], -prompt_point[0])
                elif direction == DIRECTION_LEFT:
                    # Turn the left side to the prompt (-90°)
                    angle = math.atan2(-prompt_point[0], prompt_point[1])
                elif direction == DIRECTION_RIGHT:
                    # Turn the right side to the prompt (+90°)
                    angle = math.atan2(prompt_point[0], -prompt_point[1])
                else:
                    # Turn the front to the prompt
                    angle = math.atan2(prompt_point[1], prompt_point[0])
                self.duration = abs(round(1000. * angle / self.action.rotation_speed_rad))
                self.angle = round(math.degrees(angle))

        # Compute the focus
        if focus_point is not None:
            self.focus_x = int(focus_point[0])  # Convert to python int
            self.focus_y = int(focus_point[1])
            if self.action.action_code in [ACTION_FORWARD, ACTION_BACKWARD]:
                self.speed_x = int(self.action.translation_speed[0])
            # if self.action.action_code == ACTION_BACKWARD:
            #     self.speed_x = -int(self.action.translation_speed[0])
            if self.action.action_code in [ACTION_SWIPE, ACTION_RIGHTWARD]:
                if prompt_point is not None:
                    self.speed_y = math.copysign(int(self.action.translation_speed[1]), prompt_point[1])

        # The additional fields of the command packet
        # if caution > 0:
        #     self.caution = caution  # 1: stop if there is an obstacle on the way
        #
        # if span != 40 and self.action.action_code == ACTION_SCAN:
        #     self.span = span

        # The intended translation
        if self.speed_y >= 0 or self.action.action_code in [ACTION_RIGHTWARD]:
            self.intended_translation = action.translation_speed * self.duration / 1000
        else:
            self.intended_translation = - action.translation_speed * self.duration / 1000

        # The intended yaw quaternion
        self.intended_yaw_quaternion = Quaternion.from_z_rotation(math.radians(self.angle))

        # The intended matrix of the environment relative to the robot
        self.intended_yaw_matrix = matrix44.create_from_quaternion(self.intended_yaw_quaternion)
        self.intended_displacement_matrix = matrix44.multiply(
            matrix44.create_from_translation(-self.intended_translation), self.intended_yaw_matrix)

    def command_dict(self):
        """Return a dictionary containing the command"""
        # The clock is not included because it is allocated during the enaction
        command_dict = {'action': self.action.action_code}
        if self.duration != DEFAULT_ACTION_DURATION:
            command_dict['duration'] = self.duration
        if self.angle != round(math.degrees(self.action.rotation_speed_rad * self.action.target_duration)):
            command_dict['angle'] = self.angle
        if self.focus_x is not None:
            command_dict['focus_x'] = self.focus_x
            command_dict['focus_y'] = self.focus_y
        if self.action.action_code in [ACTION_SWIPE, ACTION_RIGHTWARD]:
            command_dict['speed'] = int(self.speed_y)
        elif self.focus_x is not None:
            command_dict['speed'] = int(self.speed_x)
        if self.caution > 0:
            command_dict['caution'] = self.caution
        if self.span != 40:
            command_dict['span'] = self.span
        if self.color > 0:
            command_dict['color'] = self.color
        return command_dict

    def timeout(self):
        """Return the timeout expected from this command"""
        timeout = ENACTION_DEFAULT_TIMEOUT
        # if self.duration is not None:
        timeout = self.duration / 1000. + 2.
        # if self.angle is not None:
        # timeout = math.fabs(self.angle) / DEFAULT_YAW + 4.0  # Turn speed = 45°/s
        return timeout
