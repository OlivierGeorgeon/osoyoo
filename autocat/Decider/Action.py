import math
from pyrr import matrix44
from ..Robot.RobotDefine import FORWARD_SPEED, LATERAL_SPEED, DEFAULT_YAW

ACTION_FORWARD = '8'
ACTION_BACKWARD = '2'
ACTION_LEFTWARD = '4'
ACTION_RIGHTWARD = '6'
ACTION_TURN_LEFT = '1'
ACTION_TURN_RIGHT = '3'
ACTION_SCAN = '-'


class Action:
    action_dict = {}

    def __init__(self, action_code, displacement_matrix):
        self.action_code = action_code
        self.displacement_matrix = displacement_matrix

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

    @classmethod
    def create_or_retrieve(cls, action_code, displacement_matrix):
        """ Use this methode to create a new action or to retrieve it if it already exists """

        if action_code in cls.action_dict.keys():
            action = cls.action_dict[action_code]
            if __name__ == '__main__':
                print("Action", action, "retrieved")
        else:
            action = Action(action_code, displacement_matrix)
            cls.action_dict[action_code] = action
            if __name__ == '__main__':
                print("Action", action, "created")

        return action


# Testing Action
# py -m autocat.Decider.Action
forward_translation = matrix44.create_from_translation([-FORWARD_SPEED, 0, 0])
action_forward = Action.create_or_retrieve(ACTION_FORWARD, forward_translation)  # Create

backward_translation = matrix44.create_from_translation([FORWARD_SPEED, 0, 0])
action_backward = Action.create_or_retrieve(ACTION_BACKWARD, backward_translation)  # Create

leftward_translation = matrix44.create_from_translation([0, -LATERAL_SPEED, 0])
action_leftward = Action.create_or_retrieve(ACTION_LEFTWARD, leftward_translation)  # Create

rightward_translation = matrix44.create_from_translation([0, LATERAL_SPEED, 0])
action_rightward = Action.create_or_retrieve(ACTION_RIGHTWARD, rightward_translation)  # Create

left_rotation = matrix44.create_from_z_rotation(math.radians(DEFAULT_YAW))
action_turn_left = Action.create_or_retrieve(ACTION_TURN_LEFT, left_rotation)  # Create

right_rotation = matrix44.create_from_z_rotation(math.radians(-DEFAULT_YAW))
action_turn_right = Action.create_or_retrieve(ACTION_TURN_RIGHT, right_rotation)  # Create

action_scan = Action.create_or_retrieve(ACTION_SCAN, matrix44.create_identity())  # Create

action_scan = Action.create_or_retrieve(ACTION_SCAN, matrix44.create_identity())  # Retrieve
