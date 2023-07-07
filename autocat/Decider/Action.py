import math
import numpy as np
from ..Robot.RobotDefine import ROBOT_SETTINGS, DEFAULT_YAW, TURN_DURATION, TRANSLATE_DURATION

ACTION_FORWARD = '8'
ACTION_BACKWARD = '2'
ACTION_SWIPE = '4'
ACTION_RIGHTWARD = '6'
ACTION_TURN = '1'
ACTION_TURN_RIGHT = '3'
ACTION_CIRCUMVENT = '9'
ACTION_SCAN = '-'
ACTION_ALIGN_HEAD = '*'
ACTION_TURN_HEAD = '+'
ACTION_WATCH = 'W'
ACTIONS = [ACTION_FORWARD, ACTION_BACKWARD, ACTION_SWIPE, ACTION_RIGHTWARD, ACTION_TURN, ACTION_TURN_RIGHT,
           ACTION_SCAN, ACTION_ALIGN_HEAD, ACTION_TURN_HEAD, ACTION_CIRCUMVENT, ACTION_WATCH]


class Action:
    """A primitive action that the robot can perform"""

    def __init__(self, action_code, translation_speed, rotation_speed, target_duration):
        self.action_code = action_code
        self.translation_speed = translation_speed
        self.rotation_speed_rad = rotation_speed
        self.target_duration = target_duration

        self.simulation_duration = target_duration
        self.simulation_rotation_speed = rotation_speed

        self.simulation_step = 0
        self.simulation_time = 0.
        # print("Create action", self, "of speed", self.translation_speed, "rotation speed", self.rotation_speed_rad)

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

    def adjust_translation_speed(self, translation):
        """Set the new translation speed to the average between the previous and the argument"""
        # Adjust longitudinal speed only
        if self.action_code in [ACTION_FORWARD, ACTION_BACKWARD]:
            self.translation_speed[0] = (self.translation_speed[0] + translation[0]) / 2
            print("adjusting x speed: correction:", round(translation[0]),
                  "new x speed:", round(self.translation_speed[0]))
        # Adjust lateral speed only
        if self.action_code in [ACTION_SWIPE, ACTION_RIGHTWARD]:
            self.translation_speed[1] = (self.translation_speed[1] + translation[1]) / 2
            print("adjusting y speed: correction:", round(translation[1]),
                  "new y speed:", round(self.translation_speed[1]))


def create_actions(robot_id):
    """Create all actions"""
    x_speed = ROBOT_SETTINGS[robot_id]["forward_speed"]
    y_speed = ROBOT_SETTINGS[robot_id]["lateral_speed"]
    action_dictionary = {}

    forward_speed = np.array([x_speed, 0, 0], dtype=float)
    action_dictionary[ACTION_FORWARD] = Action(ACTION_FORWARD, forward_speed, 0, TRANSLATE_DURATION)

    backward_speed = np.array([-x_speed, 0, 0], dtype=float)
    action_dictionary[ACTION_BACKWARD] = Action(ACTION_BACKWARD, backward_speed, 0, TRANSLATE_DURATION)

    leftward_speed = np.array([0, y_speed, 0], dtype=float)
    action_dictionary[ACTION_SWIPE] = Action(ACTION_SWIPE, leftward_speed, 0, TRANSLATE_DURATION)

    rightward_speed = np.array([0, -y_speed, 0], dtype=float)
    action_dictionary[ACTION_RIGHTWARD] = Action(ACTION_RIGHTWARD, rightward_speed, 0, TRANSLATE_DURATION)

    action_dictionary[ACTION_CIRCUMVENT] = Action(ACTION_CIRCUMVENT, rightward_speed, 0, TRANSLATE_DURATION)

    null_speed = np.array([0, 0, 0], dtype=float)
    rotation_speed = math.radians(DEFAULT_YAW) / TURN_DURATION
    action_dictionary[ACTION_TURN] = Action(ACTION_TURN, null_speed, rotation_speed, TURN_DURATION)

    action_dictionary[ACTION_TURN_RIGHT] = Action(ACTION_TURN_RIGHT, null_speed, -rotation_speed, TURN_DURATION)

    action_dictionary[ACTION_SCAN] = Action(ACTION_SCAN, null_speed, 0, 2)
    action_dictionary[ACTION_ALIGN_HEAD] = Action(ACTION_ALIGN_HEAD, null_speed, 0, 1)
    action_dictionary[ACTION_TURN_HEAD] = Action(ACTION_TURN_HEAD, null_speed, 0, 1)

    action_dictionary[ACTION_WATCH] = Action(ACTION_WATCH, null_speed, 0, 1.)

    return action_dictionary


# Initializing actions with predefined speeds
# py -m autocat.Decider.Action
if __name__ == '__main__':
    create_actions()
