import json
import math
import time
import numpy as np
from .RobotDefine import DEFAULT_YAW
from ..Decider.Action import ACTION_FORWARD, ACTION_BACKWARD, ACTION_ALIGN_ROBOT, ACTION_LEFTWARD, ACTION_RIGHTWARD

ENACTION_DEFAULT_TIMEOUT = 6  # Seconds


class Enaction:
    def __init__(self, interaction, clock, focus_point, prompt_point):
        self.interaction = interaction
        self.clock = clock
        self.focus_point = focus_point
        if prompt_point is None:
            self.duration = None
            self.angle = None
        else:
            if self.interaction.action.action_code in [ACTION_FORWARD, ACTION_BACKWARD]:
                self.duration = int(np.linalg.norm(prompt_point) / self.interaction.action.translation_speed[0] * 1000)
            if self.interaction.action.action_code == ACTION_ALIGN_ROBOT:
                self.angle = int(math.degrees(math.atan2(prompt_point[1], prompt_point[0])))

    def serialize(self):
        """Return the serial representation to send to the robot"""
        serial = {'clock': self.clock, 'action': self.interaction.action.action_code}
        if self.duration is not None:
            serial['duration'] = self.duration
        if self.angle is not None:
            serial['angle'] = self.angle
        if self.focus_point is not None:
            serial['focus_x'] = int(self.focus_point[0])  # Convert to python int
            serial['focus_y'] = int(self.focus_point[1])
        if self.interaction.action.action_code == ACTION_FORWARD:
            serial['speed'] = int(self.interaction.action.translation_speed[0])
        if self.interaction.action.action_code == ACTION_BACKWARD:
            serial['speed'] = -int(self.interaction.action.translation_speed[0])
        if self.interaction.action.action_code == ACTION_LEFTWARD:
            serial['speed'] = int(self.interaction.action.translation_speed[1])
        if self.interaction.action.action_code == ACTION_RIGHTWARD:
            serial['speed'] = -int(self.interaction.action.translation_speed[1])
        return json.dumps(serial)

    def timeout(self):
        """Return the timeout of this enaction"""
        timeout = ENACTION_DEFAULT_TIMEOUT
        if self.duration is not None:
            timeout = self.duration / 1000.0 + 4.0
        if self.angle is not None:
            timeout = math.fabs(self.angle) / DEFAULT_YAW + 4.0  # Turn speed = 45°/s
        return time.time() + timeout
