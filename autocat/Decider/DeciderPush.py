########################################################################################
# This decider makes the robot stay in place and look at objects in its surrounding
# Activation 4: default.
########################################################################################

import math
from playsound import playsound
import numpy as np
from . Action import ACTION_WATCH, ACTION_TURN, ACTION_SWIPE, ACTION_FORWARD, ACTION_BACKWARD
from ..Robot.Enaction import Enaction
from . Decider import Decider, FOCUS_TOO_FAR_DISTANCE, FOCUS_TOO_TOO_FAR_DISTANCE
from . PredefinedInteractions import create_or_retrieve_primitive, OUTCOME_FOCUS_SIDE, OUTCOME_FOCUS_FRONT, OUTCOME_FOCUS_TOO_FAR
from .. Enaction.CompositeEnaction import CompositeEnaction


class DeciderPush(Decider):
    def __init__(self, workspace):
        super().__init__(workspace)

        # Give higher valence to Watch than to Swipe
        create_or_retrieve_primitive(self.primitive_interactions, workspace.actions[ACTION_SWIPE], OUTCOME_FOCUS_FRONT, 1)
        create_or_retrieve_primitive(self.primitive_interactions, workspace.actions[ACTION_FORWARD], OUTCOME_FOCUS_FRONT, 1)
        create_or_retrieve_primitive(self.primitive_interactions, workspace.actions[ACTION_WATCH], OUTCOME_FOCUS_FRONT, 2)
        self.too_far = FOCUS_TOO_FAR_DISTANCE

        self.action = self.workspace.actions[ACTION_WATCH]

    def activation_level(self):
        """The level of activation of this decider: -1: default, 5 if focus not too far """
        activation_level = -1

        # Activate when the focus is not too far
        if self.workspace.memory.egocentric_memory.focus_point is not None:
            if np.linalg.norm(self.workspace.memory.egocentric_memory.focus_point) < FOCUS_TOO_FAR_DISTANCE:
                activation_level = 5

        return activation_level

    def select_enaction(self, outcome):
        """Add the next enaction to the stack based on sequence learning and spatial modifiers"""

        # If there is an object to push
        if self.workspace.memory.egocentric_memory.focus_point is not None and outcome != OUTCOME_FOCUS_TOO_FAR:
            # Compute the prompt
            self.workspace.memory.egocentric_memory.prompt_point = self.workspace.memory.egocentric_memory.focus_point.copy()
            # First enaction: turn to the prompt
            e0 = Enaction(self.workspace.actions[ACTION_TURN], self.workspace.clock, self.workspace.memory)
            # Second enaction: move forward to the prompt
            e1 = Enaction(self.workspace.actions[ACTION_FORWARD], self.workspace.clock + 1, e0.post_memory)
            # Third enaction: turn to the prompt which is copied from the focus because it may be cleared
            e1.post_memory.egocentric_memory.prompt_point = e1.post_memory.allocentric_to_egocentric(np.array([0, 0, 0]))
            print("Return to center, egocentric position", e1.post_memory.egocentric_memory.prompt_point)
            e2 = Enaction(self.workspace.actions[ACTION_BACKWARD], self.workspace.clock + 2, e1.post_memory)
            composite_interaction = CompositeEnaction([e0, e1, e2])
        else:
            # If there is no object then watch
            print("Push decider is watching")
            composite_interaction = Enaction(self.workspace.actions[ACTION_WATCH], self.workspace.clock, self.workspace.memory)

        return composite_interaction