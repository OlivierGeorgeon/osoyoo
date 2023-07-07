import json
import math
import numpy as np
from ..Decider.Action import ACTION_FORWARD, ACTION_BACKWARD, ACTION_LEFTWARD, ACTION_RIGHTWARD, \
    ACTION_TURN, ACTION_TURN_RIGHT, ACTION_TURN_HEAD, ACTION_WATCH
from .RobotDefine import DEFAULT_YAW

ENACTION_DEFAULT_TIMEOUT = 6  # Seconds


class Command:
    """A command to send to the robot"""
    def __init__(self, action, clock, prompt_point, focus_point):
        self.action = action
        self.clock = clock
        self.duration = None
        self.angle = None
        self.focus_x = None
        self.focus_y = None
        self.speed = None

        if prompt_point is not None:
            if self.action.action_code in [ACTION_FORWARD, ACTION_BACKWARD]:
                self.duration = int(np.linalg.norm(prompt_point) / math.fabs(self.action.translation_speed[0]) * 1000)
            if self.action.action_code in [ACTION_LEFTWARD, ACTION_RIGHTWARD]:
                self.duration = int(np.linalg.norm(prompt_point) / math.fabs(self.action.translation_speed[1]) * 1000)
            if self.action.action_code in [ACTION_TURN_HEAD, ACTION_TURN_RIGHT, ACTION_TURN]:
                self.angle = int(math.degrees(math.atan2(prompt_point[1], prompt_point[0])))
        else:
            # Default backward 0.5s
            if self.action.action_code in [ACTION_BACKWARD]:
                self.duration = 500
            # Default sidewards 1.5s
            if self.action.action_code in [ACTION_LEFTWARD, ACTION_RIGHTWARD]:
                self.duration = 1000  # 1500
        if self.action.action_code in [ACTION_WATCH]:
            self.duration = 5000

        if focus_point is not None:
            self.focus_x = int(focus_point[0])  # Convert to python int
            self.focus_y = int(focus_point[1])
            if self.action.action_code == ACTION_FORWARD:
                self.speed = int(self.action.translation_speed[0])
            if self.action.action_code == ACTION_BACKWARD:
                self.speed = -int(self.action.translation_speed[0])
            if self.action.action_code in [ACTION_LEFTWARD, ACTION_RIGHTWARD]:
                self.speed = int(self.action.translation_speed[1])
            # if self.action.action_code == ACTION_RIGHTWARD:
            #     self.speed = -int(self.action.translation_speed[1])

    def serialize(self):
        """Return the command string to send to the robot"""
        command_dict = {'clock': self.clock, 'action': self.action.action_code}
        if self.duration is not None:
            command_dict['duration'] = self.duration
        if self.angle is not None:
            command_dict['angle'] = self.angle
        if self.focus_x is not None:
            command_dict['focus_x'] = self.focus_x
            command_dict['focus_y'] = self.focus_y
        if self.speed is not None:
            command_dict['speed'] = self.speed
        return json.dumps(command_dict)

    def timeout(self):
        """Return the timeout expected from this command"""
        timeout = ENACTION_DEFAULT_TIMEOUT
        if self.duration is not None:
            timeout = self.duration / 1000.0 + 4.0
        if self.angle is not None:
            timeout = math.fabs(self.angle) / DEFAULT_YAW + 4.0  # Turn speed = 45°/s
        return timeout

