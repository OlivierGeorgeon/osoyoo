########################################################################################
# This proposer makes the robot push an object when it has the focus
# Activation 2: when the robot is angry
########################################################################################

import math
import numpy as np
from pyrr import vector, Vector3
from . Action import ACTION_TURN, ACTION_FORWARD, ACTION_BACKWARD, ACTION_SCAN
from ..Robot.Enaction import Enaction
from ..Robot.Command import DIRECTION_BACK
from . Proposer import Proposer
from ..Integrator.OutcomeCode import FOCUS_TOO_FAR_DISTANCE
from .. Enaction.CompositeEnaction import CompositeEnaction
from ..Memory import EMOTION_ANGRY
from . Interaction import OUTCOME_FLOOR

STEP_INIT = 0
STEP_WITHDRAW = 1


class ProposerPush(Proposer):
    def __init__(self, workspace):
        super().__init__(workspace)
        # self.too_far = FOCUS_TOO_FAR_DISTANCE
        # self.action = self.workspace.actions[ACTION_SCAN]
        self.step = STEP_INIT

    def activation_level(self):
        """The level of activation of this decider: 0: default, 4 if focus inside terrain, 3 for withdrawal"""
        # activation_level = 0
        # If focus is not None and is inside terrain
        if self.is_to_push():
            return 4
        elif self.step == STEP_WITHDRAW:
            return 3  # May compete with ProposerExplore to return directly to origin
        return 0

    def select_enaction(self, enaction):
        """Add the next enaction to the stack based on sequence learning and spatial modifiers"""
        e_memory = self.workspace.memory.save()
        e_memory.emotion_code = EMOTION_ANGRY

        # If there is an object to push
        if self.is_to_push() and enaction.outcome_code != OUTCOME_FLOOR:
                # e_memory.phenomenon_memory.is_inside_terrain(e_memory.egocentric_to_terrain_centric(
                #     self.workspace.memory.egocentric_memory.focus_point)):
            # Start pushing
            # if e_memory.egocentric_memory.focus_point is not None and enaction.outcome_code != OUTCOME_FLOOR:
            ego_destination = vector.set_length(e_memory.egocentric_memory.focus_point, 1200)
            e_memory.egocentric_memory.prompt_point = ego_destination
            # If object in front modulo 10° then push
            if abs(math.atan2(ego_destination[1], math.fabs(ego_destination[0]))) < 0.175:
                composite_enaction = Enaction(self.workspace.actions[ACTION_FORWARD], e_memory)
                self.step = STEP_WITHDRAW
            # If object not in front then turn toward object
            else:
                composite_enaction = Enaction(self.workspace.actions[ACTION_TURN], e_memory)
            # else:
            #     # If there is no object then scan (probably never happens)
            #     print("DeciderPush is scanning")
            #     composite_enaction = Enaction(self.workspace.actions[ACTION_SCAN], e_memory, span=10)

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
