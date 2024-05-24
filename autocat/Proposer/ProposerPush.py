########################################################################################
# This proposer makes the robot push an object when it has the focus
# Activation: 2.
# EMOTION_VIGILANT behavior (Noradrenaline)
########################################################################################

import math
import numpy as np
from pyrr import vector, Vector3
from . Action import ACTION_TURN, ACTION_FORWARD, ACTION_BACKWARD
from ..Robot.Enaction import Enaction
from ..Robot.Command import DIRECTION_BACK
from . Proposer import Proposer
from .. Enaction.CompositeEnaction import CompositeEnaction
from ..Memory import EMOTION_VIGILANCE
from ..Memory.BodyMemory import NORADRENALINE
from . Interaction import OUTCOME_FLOOR
from ..Utils import assert_almost_equal_angles

STEP_INIT = 0
STEP_WITHDRAW = 1


class ProposerPush(Proposer):
    def __init__(self, workspace):
        super().__init__(workspace)
        self.step = STEP_INIT

    def activation_level(self):
        """The level of activation of this decider: 0: default, 4 if focus inside terrain, 3 for withdrawal"""

        return self.workspace.memory.body_memory.neurotransmitters[NORADRENALINE]

    def propose_enaction(self):
        """Add the next enaction to the stack based on sequence learning and spatial modifiers"""
        enaction = self.workspace.enaction

        e_memory = self.workspace.memory.save()
        e_memory.emotion_code = EMOTION_VIGILANCE

        # If there is an object to push
        if self.is_to_push() and enaction.outcome_code != OUTCOME_FLOOR:
            # Start pushing
            ego_destination = vector.set_length(e_memory.egocentric_memory.focus_point, 1200)
            e_memory.egocentric_memory.prompt_point = ego_destination
            # If object in front modulo 10° then push
            # if abs(math.atan2(ego_destination[1], math.fabs(ego_destination[0]))) < 0.175:
            if assert_almost_equal_angles(math.atan2(ego_destination[1], ego_destination[0]), 0, 10):
                composite_enaction = Enaction(self.workspace.actions[ACTION_FORWARD], e_memory)
                self.step = STEP_WITHDRAW
            # If object not in front then turn toward object
            else:
                composite_enaction = Enaction(self.workspace.actions[ACTION_TURN], e_memory)

        # Withdraw step
        elif self.step == STEP_WITHDRAW:
            ego_watch_point = self.workspace.memory.terrain_centric_to_egocentric(np.array([0, 0, 0]))
            e_memory.egocentric_memory.prompt_point = ego_watch_point
            # First enaction: re-align the back toward the watch point
            e0 = Enaction(self.workspace.actions[ACTION_TURN], e_memory, direction=DIRECTION_BACK)
            # Second enaction: move back to the prompt
            e1 = Enaction(self.workspace.actions[ACTION_BACKWARD], e0.predicted_memory.save())
            composite_enaction = CompositeEnaction([e0, e1])
            self.step = STEP_INIT

        # Otherwise don't propose an enaction (OUTCOME_FLOOR)
        else:
            composite_enaction = None

        return composite_enaction

    def is_to_push(self):
        """Return True if the focus is not None and is inside the terrain"""
        return self.workspace.memory.phenomenon_memory.is_inside_terrain(
                    self.workspace.memory.egocentric_to_terrain_centric(
                        self.workspace.memory.egocentric_memory.focus_point))
