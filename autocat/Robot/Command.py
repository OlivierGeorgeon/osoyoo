import json
import math
from pyrr import Quaternion, matrix44
from ..Decider.Action import ACTION_FORWARD, ACTION_BACKWARD, ACTION_SWIPE, ACTION_RIGHTWARD, ACTION_TURN, \
    ACTION_TURN_HEAD
from .RobotDefine import DEFAULT_ACTION_DURATION
from ..Utils import translation_quaternion_to_matrix

ENACTION_MIN_TIMEOUT = 2.  # Seconds
DIRECTION_FRONT = 0  # Direction code to go to turn to the prompt
DIRECTION_BACK = 1
DIRECTION_LEFT = 2
DIRECTION_RIGHT = 3


class Command:
    """A command to send to the robot"""
    def __init__(self, action, clock, prompt_point, focus_point, direction, span, color, caution):

        # The required fields
        self.action = action
        self.clock = clock
        self.duration = action.target_duration * 1000  # Default duration
        self.yaw = round(math.degrees(action.rotation_speed_rad * action.target_duration))
        self.speed = self.action.translation_speed.copy()
        # self.speed_y = self.action.translation_speed[1]
        self.color = color
        self.caution = caution
        self.span = span

        # The focus is optional
        if focus_point is None:
            self.focus = None
        else:
            self.focus = focus_point.copy()
        # self.focus_y = None

        # Override the default duration and yaw on the basis of the prompt
        if prompt_point is not None:
            if self.action.action_code in [ACTION_FORWARD, ACTION_BACKWARD]:
                self.duration = int(math.fabs(prompt_point[0] / self.action.translation_speed[0] * 1000))
            if self.action.action_code in [ACTION_SWIPE, ACTION_RIGHTWARD]:
                self.duration = int(math.fabs(prompt_point[1] / self.action.translation_speed[1] * 1000))
                self.speed[1] = math.copysign(int(self.action.translation_speed[1]), prompt_point[1])
                # if prompt_point[1] < 0:
                #     self.speed[1] = -int(self.action.translation_speed[1])  # Negative speed makes swipe right
            if self.action.action_code in [ACTION_TURN_HEAD, ACTION_TURN]:
                if direction == DIRECTION_BACK:
                    # Turn the back to the prompt
                    yaw = -math.atan2(prompt_point[1], -prompt_point[0])
                elif direction == DIRECTION_LEFT:
                    # Turn the left side to the prompt (-90°)
                    yaw = math.atan2(-prompt_point[0], prompt_point[1])
                elif direction == DIRECTION_RIGHT:
                    # Turn the right side to the prompt (+90°)
                    yaw = math.atan2(prompt_point[0], -prompt_point[1])
                else:
                    # Turn the front to the prompt
                    yaw = math.atan2(prompt_point[1], prompt_point[0])
                self.duration = abs(round(1000. * yaw / self.action.rotation_speed_rad))
                self.yaw = round(math.degrees(yaw))

        # Compute the focus
        # if focus_point is not None:
        #     self.focus_x = int(focus_point[0])  # Convert to python int
        #     self.focus_y = int(focus_point[1])
            # if self.action.action_code in [ACTION_FORWARD, ACTION_BACKWARD]:
            #     self.speed[0] = int(self.action.translation_speed[0])
        # if self.action.action_code in [ACTION_SWIPE, ACTION_RIGHTWARD] and prompt_point is not None:
        #     self.speed[1] = math.copysign(int(self.action.translation_speed[1]), prompt_point[1])

        # The intended translation
        if self.speed[1] >= 0 or self.action.action_code in [ACTION_RIGHTWARD]:
            self.intended_translation = action.translation_speed * self.duration / 1000
        else:
            self.intended_translation = - action.translation_speed * self.duration / 1000

        # The intended yaw quaternion
        self.intended_yaw_quaternion = Quaternion.from_z_rotation(math.radians(self.yaw))

        # The intended matrix of the environment's displacement relative to the robot
        self.intended_displacement_matrix = translation_quaternion_to_matrix(-self.intended_translation,
                                                                             self.intended_yaw_quaternion.inverse)

    def serialize(self):
        """Return the json string to send to the robot"""
        command_dict = {'clock': self.clock,  'action': self.action.action_code}
        # Don't send the optional values when not needed
        if self.duration != DEFAULT_ACTION_DURATION and self.action.action_code != ACTION_TURN:
            command_dict['duration'] = self.duration
        if self.yaw != round(math.degrees(self.action.rotation_speed_rad * self.action.target_duration)):
            command_dict['angle'] = self.yaw
        if self.focus is not None:
            command_dict['focus_x'] = int(self.focus[0])
            command_dict['focus_y'] = int(self.focus[1])
        # Send the speed if SWIPE or focus
        if self.action.action_code in [ACTION_SWIPE, ACTION_RIGHTWARD]:
            command_dict['speed'] = int(self.speed[1])
        elif self.focus is not None:
            command_dict['speed'] = int(self.speed[0])
        if self.caution > 0:
            command_dict['caution'] = self.caution
        if self.span != 40:
            command_dict['span'] = self.span
        if self.color > 0:
            command_dict['color'] = self.color
        return json.dumps(command_dict)

    def timeout(self):
        """Return the timeout expected from this command"""
        # timeout = ENACTION_DEFAULT_TIMEOUT
        # if self.duration is not None:
        timeout = self.duration / 1000. + ENACTION_MIN_TIMEOUT
        # if self.angle is not None:
        # timeout = math.fabs(self.angle) / DEFAULT_YAW + 4.0  # Turn speed = 45°/s
        return timeout
