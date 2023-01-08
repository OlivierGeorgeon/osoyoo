import math
import numpy as np
from ..Robot.RobotDefine import FORWARD_SPEED, LATERAL_SPEED, DEFAULT_YAW

ACTION_FORWARD = '8'
ACTION_BACKWARD = '2'
ACTION_LEFTWARD = '4'
ACTION_RIGHTWARD = '6'
ACTION_TURN_LEFT = '1'
ACTION_TURN_RIGHT = '3'
ACTION_SCAN = '-'


class Action:
    """A primitive action that the robot can perform"""

    def __init__(self, action_code, translation_speed, rotation_speed, target_yaw):
        self.action_code = action_code
        self.translation_speed = translation_speed
        self.rotation_speed_rad = rotation_speed
        self.target_yaw = target_yaw
        print("Create action", self, "of speed", self.translation_speed)

    def __str__(self):
        """ Print the action as its action_code"""
        return self.action_code

    def __hash__(self):
        """ The hash is necessary to use actions as keys in a dictionary """
        return self.action_code.__hash__()

    def __eq__(self, other):
        """ Actions are equal if they have the same action_code """
        if isinstance(other, self.__class__):
            return self.action_code == other.action_code
        else:
            return False


def create_actions():
    """Create all actions"""
    action_dictionary = {}

    forward_speed = np.array([FORWARD_SPEED, 0, 0], dtype=float)
    action_dictionary[ACTION_FORWARD] = Action(ACTION_FORWARD, forward_speed, 0, 0)

    backward_speed = np.array([-FORWARD_SPEED, 0, 0], dtype=float)
    action_dictionary[ACTION_BACKWARD] = Action(ACTION_BACKWARD, backward_speed, 0, 0)

    leftward_speed = np.array([0, LATERAL_SPEED, 0], dtype=float)
    action_dictionary[ACTION_LEFTWARD] = Action(ACTION_LEFTWARD, leftward_speed, 0, 0)

    rightward_speed = np.array([0, -LATERAL_SPEED, 0], dtype=float)
    action_dictionary[ACTION_RIGHTWARD] = Action(ACTION_RIGHTWARD, rightward_speed, 0, 0)

    null_speed = np.array([0, 0, 0], dtype=float)
    rotation_speed = math.radians(DEFAULT_YAW) / 2.  # Based on estimated turn duration
    action_dictionary[ACTION_TURN_LEFT] = Action(ACTION_TURN_LEFT, null_speed, rotation_speed, DEFAULT_YAW)

    action_dictionary[ACTION_TURN_RIGHT] = Action(ACTION_TURN_RIGHT, null_speed, -rotation_speed, -DEFAULT_YAW)

    action_dictionary[ACTION_SCAN] = Action(ACTION_SCAN, null_speed, 0, 0)

    return action_dictionary


# Initializing actions with predefined speeds
# py -m autocat.Decider.Action
if __name__ == '__main__':
    create_actions()
