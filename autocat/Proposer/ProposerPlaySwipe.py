########################################################################################
# This proposer makes the robot play by swiping to an object and back
# Activation: 5
# EMOTION_CONTENT (Serotonin)
########################################################################################

import math
import numpy as np
from pyrr import vector, Vector3
from . Action import ACTION_TURN, ACTION_SWIPE
from ..Robot.Enaction import Enaction
from ..Robot.RobotDefine import ROBOT_HEAD_X
from . Proposer import Proposer
from ..Memory import EMOTION_CONTENT
from ..Memory.BodyMemory import EXCITATION_LOW
from . Interaction import OUTCOME_FLOOR, OUTCOME_FOCUS_TOO_FAR
from ..Robot.Command import DIRECTION_LEFT, DIRECTION_RIGHT

STEP_INIT = 0
STEP_WITHDRAW_TO_RIGHT = 1
STEP_WITHDRAW_TO_LEFT = 2

PLAY_DISTANCE_CLOSE = 200  # Between robot center and object center
PLAY_DISTANCE_WITHDRAW = 250  # From where the robot has stopped


class ProposerPlaySwipe(Proposer):
    def __init__(self, workspace):
        super().__init__(workspace)
        self.step = STEP_INIT

    def activation_level(self):
        """The level of activation of this decider: 0: default, 5 if excited and object to play with """
        if self.workspace.memory.body_memory.excitation > EXCITATION_LOW and \
                (self.is_to_play() or self.step in [STEP_WITHDRAW_TO_RIGHT, STEP_WITHDRAW_TO_LEFT]):
            return 5
        return 0

    def select_enaction(self, enaction):
        """Add the next enaction to the stack based on sequence learning and spatial modifiers"""
        e_memory = self.workspace.memory.save()
        e_memory.emotion_code = EMOTION_CONTENT

        # Withdraw step
        if self.step == STEP_WITHDRAW_TO_RIGHT:
            e_memory.egocentric_memory.prompt_point = np.array([0, -PLAY_DISTANCE_WITHDRAW, 0])
            self.step = STEP_INIT
            return Enaction(self.workspace.actions[ACTION_SWIPE], e_memory)
        elif self.step == STEP_WITHDRAW_TO_LEFT:
            e_memory.egocentric_memory.prompt_point = np.array([0, PLAY_DISTANCE_WITHDRAW, 0])
            self.step = STEP_INIT
            return Enaction(self.workspace.actions[ACTION_SWIPE], e_memory)

        # If there is an object to play with
        elif self.is_to_play() and enaction.outcome_code not in [OUTCOME_FLOOR, OUTCOME_FOCUS_TOO_FAR]:
            # If object on the side then play
            if abs(e_memory.egocentric_memory.focus_point[0] - ROBOT_HEAD_X) < 40:
                # If object on the left
                if e_memory.egocentric_memory.focus_point[1] > PLAY_DISTANCE_CLOSE:
                    self.step = STEP_WITHDRAW_TO_RIGHT
                    ego_destination = np.array([0, e_memory.egocentric_memory.focus_point[1] - PLAY_DISTANCE_CLOSE, 0])
                    e_memory.egocentric_memory.prompt_point = ego_destination
                    return Enaction(self.workspace.actions[ACTION_SWIPE], e_memory)
                # If object on the right
                elif e_memory.egocentric_memory.focus_point[1] < -PLAY_DISTANCE_CLOSE:
                    self.step = STEP_WITHDRAW_TO_LEFT
                    ego_destination = np.array([0, e_memory.egocentric_memory.focus_point[1] + PLAY_DISTANCE_CLOSE, 0])
                    e_memory.egocentric_memory.prompt_point = ego_destination
                    return Enaction(self.workspace.actions[ACTION_SWIPE], e_memory)
                # If object too close then don't propose an action
                else:
                    print("Object too close for swipe play")
                    return None
            # If object not on the side then turn
            else:
                # e_memory.egocentric_memory.prompt_point = np.array([0, e_memory.egocentric_memory.focus_point[1], 0])
                e_memory.egocentric_memory.prompt_point = e_memory.egocentric_memory.focus_point.copy()
                # If Object on the left then turn the left side towards the object
                if e_memory.egocentric_memory.focus_point[1] > 0:
                    return Enaction(self.workspace.actions[ACTION_TURN], e_memory, direction=DIRECTION_LEFT)
                # If Object on the right then turn the right side toward the object
                else:
                    return Enaction(self.workspace.actions[ACTION_TURN], e_memory, direction=DIRECTION_RIGHT)
        # Otherwise don't propose an enaction (OUTCOME_FLOOR)
        else:
            return None

    def is_to_play(self):
        """Return True if the focus is not None and not too far"""
        if self.workspace.memory.egocentric_memory.focus_point is None:
            return False

        if np.linalg.norm(self.workspace.memory.egocentric_memory.focus_point) > 800:  #FOCUS_TOO_FAR_DISTANCE:
            return False

        return True
