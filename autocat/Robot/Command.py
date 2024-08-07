import json
import math
from ..Proposer.Action import ACTION_FORWARD, ACTION_BACKWARD, ACTION_SWIPE, ACTION_RIGHTWARD, ACTION_TURN, \
    ACTION_TURN_HEAD, ACTION_SCAN
from .RobotDefine import DEFAULT_ACTION_DURATION

ENACTION_MIN_TIMEOUT = 3.  # Seconds
DIRECTION_FRONT = 0  # Direction code to go to turn to the prompt
DIRECTION_BACK = 1
DIRECTION_LEFT = 2
DIRECTION_RIGHT = 3


class Command:
    """A command to send to the robot"""
    def __init__(self, action, memory, direction, span, caution):
        # clock = memory.clock
        prompt_point = memory.egocentric_memory.prompt_point
        # focus_point = memory.egocentric_memory.focus_point
        # color = memory.body_memory.emotion_code()

        # The fields that are not None
        self.action = action
        self.clock = memory.clock
        self.duration = action.target_duration * 1000  # Default duration
        self.yaw = round(math.degrees(action.rotation_speed_rad * action.target_duration))
        self.speed = self.action.translation_speed.copy()
        self.rotation_speed = 0
        self.color = memory.body_memory.emotion_code()
        self.caution = caution
        self.span = span

        # The focus is optional
        if memory.egocentric_memory.focus_point is None:
            self.focus = None
        else:
            self.focus = memory.egocentric_memory.focus_point.copy()

        # Override the default duration and yaw on the basis of the prompt
        if prompt_point is not None:
            if self.action.action_code in [ACTION_FORWARD, ACTION_BACKWARD]:
                self.duration = int(math.fabs(prompt_point[0] / self.action.translation_speed[0] * 1000))
            if self.action.action_code in [ACTION_SWIPE, ACTION_RIGHTWARD]:
                self.duration = int(math.fabs(prompt_point[1] / self.action.translation_speed[1] * 1000))
                self.speed[1] = math.copysign(int(self.action.translation_speed[1]), prompt_point[1])
            if self.action.action_code in [ACTION_TURN_HEAD, ACTION_TURN]:
                if direction == DIRECTION_BACK:
                    # Turn the back to the prompt
                    yaw_rad = -math.atan2(prompt_point[1], -prompt_point[0])
                elif direction == DIRECTION_LEFT:
                    # Turn the left side to the prompt (-90°)
                    yaw_rad = math.atan2(-prompt_point[0], prompt_point[1])
                elif direction == DIRECTION_RIGHT:
                    # Turn the right side to the prompt (+90°)
                    yaw_rad = math.atan2(prompt_point[0], -prompt_point[1])
                else:
                    # Turn the front to the prompt
                    yaw_rad = math.atan2(prompt_point[1], prompt_point[0])
                self.duration = abs(round(1000. * yaw_rad / self.action.rotation_speed_rad))
                self.yaw = round(math.degrees(yaw_rad))
        self.rotation_speed_rad = math.copysign(self.action.rotation_speed_rad, self.yaw)  # For simulator

    def serialize(self):
        """Return the json string to send to the robot"""
        command_dict = {'clock': self.clock,  'action': self.action.action_code}
        # Don't send the optional values when not needed
        if self.duration != DEFAULT_ACTION_DURATION and self.action.action_code not in [ACTION_TURN, ACTION_SCAN]:
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
        if self.span != 30:
            command_dict['span'] = self.span
        if self.color > 0:
            command_dict['color'] = self.color
        return json.dumps(command_dict)

    def timeout(self):
        """Return the timeout expected from this command in seconds"""
        timeout = self.duration / 1000. + ENACTION_MIN_TIMEOUT
        # print("Time out", timeout)
        return timeout
