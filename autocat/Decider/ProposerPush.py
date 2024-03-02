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
from ..Memory.Memory import EMOTION_ANGRY
from . Interaction import OUTCOME_FLOOR

STEP_INIT = 0
STEP_PUSH = 1


class ProposerPush(Proposer):
    def __init__(self, workspace):
        super().__init__(workspace)
        self.too_far = FOCUS_TOO_FAR_DISTANCE
        self.action = self.workspace.actions[ACTION_SCAN]
        self.step = STEP_INIT

    def activation_level(self):
        """The level of activation of this decider: -1: default, 5 if focus inside terrain"""
        activation_level = 0
        # If focus is not None and is inside terrain
        if self.workspace.memory.egocentric_memory.focus_point is not None and self.workspace.memory.phenomenon_memory.is_inside_terrain(self.workspace.memory.egocentric_to_terrain_centric(self.workspace.memory.egocentric_memory.focus_point)):
            activation_level = 4
        # if self.workspace.memory.emotion_code == EMOTION_ANGRY:
        #     activation_level = 4
        # Activate during the withdraw step
        if self.step == STEP_PUSH:
            activation_level = 3  # May return to deciderExplore to return directly to origin
        return activation_level

    def select_enaction(self, enaction):
        """Add the next enaction to the stack based on sequence learning and spatial modifiers"""
        composite_enaction = None
        e_memory = self.workspace.memory.save()
        e_memory.emotion_code = EMOTION_ANGRY
        # If there is an object to push
        if self.workspace.memory.egocentric_memory.focus_point is not None and self.workspace.memory.phenomenon_memory.is_inside_terrain(self.workspace.memory.egocentric_to_terrain_centric(self.workspace.memory.egocentric_memory.focus_point)):
        # if self.step == STEP_INIT:
            # Start pushing
            if e_memory.egocentric_memory.focus_point is not None and enaction.outcome_code != OUTCOME_FLOOR:
                ego_destination = vector.set_length(e_memory.egocentric_memory.focus_point, 1200)
                e_memory.egocentric_memory.prompt_point = ego_destination
                # If object in front modulo 10° then push
                if abs(math.atan2(ego_destination[1], math.fabs(ego_destination[0]))) < 0.175:
                    composite_enaction = Enaction(self.workspace.actions[ACTION_FORWARD], e_memory)
                    self.step = STEP_PUSH
                # If object not in front then turn toward object
                else:
                    composite_enaction = Enaction(self.workspace.actions[ACTION_TURN], e_memory)
            else:
                # If there is no object then watch (probably never happens)
                print("DeciderPush is watching")
                composite_enaction = Enaction(self.workspace.actions[ACTION_SCAN], e_memory, span=10)
        elif self.step == STEP_PUSH:
            # Start withdrawing
            # The first enaction: turn the back to the prompt
            # origin = self.workspace.memory.phenomenon_memory.watch_point()  # Birth place or arena center
            # e_memory.egocentric_memory.prompt_point = e_memory.allocentric_to_egocentric(origin)
            ego_watch_point = self.workspace.memory.terrain_centric_to_egocentric(np.array([0, 0, 0]))
            e_memory.egocentric_memory.prompt_point = ego_watch_point
            e0 = Enaction(self.workspace.actions[ACTION_TURN], e_memory, direction=DIRECTION_BACK)
            # Second enaction: move forward to the prompt
            e1 = Enaction(self.workspace.actions[ACTION_BACKWARD], e0.predicted_memory.save())
            composite_enaction = CompositeEnaction([e0, e1])
            self.step = STEP_INIT

        return composite_enaction
