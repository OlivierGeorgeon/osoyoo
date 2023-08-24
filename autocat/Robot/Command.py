import json
import math
import numpy as np
from pyrr import Quaternion, matrix44
from ..Decider.Action import ACTION_FORWARD, ACTION_BACKWARD, ACTION_SWIPE, ACTION_RIGHTWARD, \
    ACTION_TURN, ACTION_TURN_HEAD, ACTION_WATCH, ACTION_SCAN
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
        self.caution = None  # 1  # Check for obstacles when moving forward
        self.span = None

        if prompt_point is not None:
            if self.action.action_code in [ACTION_FORWARD, ACTION_BACKWARD]:
                self.duration = int(np.linalg.norm(prompt_point) / math.fabs(self.action.translation_speed[0]) * 1000)
            if self.action.action_code in [ACTION_SWIPE]:
                self.duration = int(np.linalg.norm(prompt_point) / math.fabs(self.action.translation_speed[1]) * 1000)
                if prompt_point[1] < 0:
                    self.speed = -int(self.action.translation_speed[1])  # Negative speed makes swipe right
            if self.action.action_code in [ACTION_TURN_HEAD, ACTION_TURN]:  # ACTION_TURN_RIGHT
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

        if focus_point is not None:
            self.focus_x = int(focus_point[0])  # Convert to python int
            self.focus_y = int(focus_point[1])
            if self.action.action_code == ACTION_FORWARD:
                self.speed = int(self.action.translation_speed[0])
            if self.action.action_code == ACTION_BACKWARD:
                self.speed = -int(self.action.translation_speed[0])
            if self.action.action_code in [ACTION_SWIPE, ACTION_RIGHTWARD]:
                self.speed = int(self.action.translation_speed[1])
                if prompt_point is not None:  #  and prompt_point[1] > 0:
                    self.speed = math.copysign(int(self.action.translation_speed[1]), prompt_point[1])
            #     else:
            #         self.speed = -int(self.action.translation_speed[1])  # Negative speed makes swipe right
            # if self.action.action_code == ACTION_RIGHTWARD:
            #     self.speed = int(self.action.translation_speed[1])

        # The anticipated displacement
        if self.duration is None:
            if self.speed is None or self.speed > 0:
                self.anticipated_translation = action.translation_speed * action.target_duration
            else:
                self.anticipated_translation = - action.translation_speed * action.target_duration
        else:
            if self.speed is None or self.speed > 0:
                self.anticipated_translation = action.translation_speed * self.duration / 1000
            else:
                self.anticipated_translation = - action.translation_speed * self.duration / 1000

        if self.angle is None:
            self.anticipated_yaw_quaternion = Quaternion.from_z_rotation(action.rotation_speed_rad * action.target_duration)
        else:
            self.anticipated_yaw_quaternion = Quaternion.from_z_rotation(math.radians(self.angle))

        self.anticipated_yaw_matrix = matrix44.create_from_inverse_of_quaternion(self.anticipated_yaw_quaternion)
        self.anticipated_displacement_matrix = matrix44.multiply(matrix44.create_from_translation(-self.anticipated_translation),
                                                     self.anticipated_yaw_matrix)

        if self.action.action_code == ACTION_FORWARD:
            self.caution = 1  # Will stop if there is an obstaction on the way

        # if self.action.action_code == ACTION_SCAN:
        #     self.span = 10

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
        if self.caution is not None:
            command_dict['caution'] = self.caution
        if self.span is not None:
            command_dict['span'] = self.span
        return json.dumps(command_dict)

    def timeout(self):
        """Return the timeout expected from this command"""
        timeout = ENACTION_DEFAULT_TIMEOUT
        if self.duration is not None:
            timeout = self.duration / 1000.0 + 4.0
        if self.angle is not None:
            timeout = math.fabs(self.angle) / DEFAULT_YAW + 4.0  # Turn speed = 45°/s
        return timeout

