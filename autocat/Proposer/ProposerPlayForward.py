########################################################################################
# This proposer makes the robot play by going to an object and back
# Activation 5: Makes the robot HAPPY
########################################################################################

import math
import numpy as np
from pyrr import vector, Vector3
from . Action import ACTION_TURN, ACTION_FORWARD, ACTION_BACKWARD, ACTION_SWIPE, ACTION_SCAN
from ..Robot.Enaction import Enaction
from ..Robot.Command import DIRECTION_BACK
from . Proposer import Proposer
from .. Enaction.CompositeEnaction import CompositeEnaction
from ..Memory import EMOTION_HAPPY
from ..Memory.BodyMemory import EXCITATION_LOW
from . Interaction import OUTCOME_FLOOR, OUTCOME_FOCUS_TOO_FAR
from ..Utils import assert_almost_equal_angles
from ..Integrator.OutcomeCode import FOCUS_TOO_FAR_DISTANCE

STEP_INIT = 0
STEP_WITHDRAW = 1

PLAY_DISTANCE_CLOSE = 200  # Between robot center and object center
PLAY_DISTANCE_WITHDRAW = 250  # From where the robot has stopped


class ProposerPlayForward(Proposer):
    def __init__(self, workspace):
        super().__init__(workspace)
        self.step = STEP_INIT

    def activation_level(self):
        """The level of activation of this decider: 0: default, 5 if excited and object to play with """
        if self.workspace.memory.body_memory.excitation > EXCITATION_LOW and \
                (self.is_to_play() or self.step == STEP_WITHDRAW):
            return 5

        # if self.is_to_play() and self.workspace.memory.body_memory.excitation > EXCITATION_LOW:
        #     return 5
        # elif self.step == STEP_WITHDRAW:
        #     return 5

        return 0

    def select_enaction(self, enaction):
        """Add the next enaction to the stack based on sequence learning and spatial modifiers"""
        e_memory = self.workspace.memory.save()
        e_memory.emotion_code = EMOTION_HAPPY

        # Withdraw step
        if self.step == STEP_WITHDRAW:
            e_memory.egocentric_memory.prompt_point = np.array([-PLAY_DISTANCE_WITHDRAW, 0, 0])
            self.step = STEP_INIT
            return Enaction(self.workspace.actions[ACTION_BACKWARD], e_memory)

        # If there is an object to play with
        elif self.is_to_play() and enaction.outcome_code not in [OUTCOME_FLOOR, OUTCOME_FOCUS_TOO_FAR]:
            # If object in front then play
            if abs(e_memory.egocentric_memory.focus_point[1]) < 40:
                self.step = STEP_WITHDRAW
                ego_destination = np.array([e_memory.egocentric_memory.focus_point[0] - PLAY_DISTANCE_CLOSE, 0, 0])
                e_memory.egocentric_memory.prompt_point = ego_destination
                return Enaction(self.workspace.actions[ACTION_FORWARD], e_memory)
            # If angle lower than 10° then swipe
            elif assert_almost_equal_angles(math.atan2(e_memory.egocentric_memory.focus_point[1],
                                                       e_memory.egocentric_memory.focus_point[0]), 0, 10):
                e_memory.egocentric_memory.prompt_point = e_memory.egocentric_memory.focus_point.copy()
                return Enaction(self.workspace.actions[ACTION_SWIPE], e_memory)
            # If angle greater than 10° then turn
            else:
                e_memory.egocentric_memory.prompt_point = e_memory.egocentric_memory.focus_point.copy()
                return Enaction(self.workspace.actions[ACTION_TURN], e_memory)

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
