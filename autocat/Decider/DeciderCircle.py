########################################################################################
# This decider makes the robot circle around an echo object or a territory delimited by a line
# Activation 1: default. 3: focus
########################################################################################

import numpy as np
from . Action import ACTION_TURN
from ..Robot.Enaction import Enaction
from . Decider import Decider, FOCUS_TOO_FAR_DISTANCE
from . PredefinedInteractions import OUTCOME_FOCUS_TOO_FAR
from ..Memory.Memory import EMOTION_HAPPY
from ..Memory.BodyMemory import EXCITATION_LOW


class DeciderCircle(Decider):
    def __init__(self, workspace):
        """ Creating our agent """
        super().__init__(workspace)

    def activation_level(self):
        """Return the activation level of this decider/ 1: default; 3 if focus not too far and excited"""
        activation_level = 1  # Is the decider by default
        if self.workspace.memory.emotion_code == EMOTION_HAPPY:
            activation_level = 2
        return activation_level

    def select_enaction(self, outcome):
        """Add the next enaction to the stack based on sequence learning and spatial modifiers"""

        # Call the sequence learning mechanism to select the next action
        self.select_action(outcome)

        # Set the spatial modifiers
        if self.action.action_code in [ACTION_TURN]:
            # Turn to the direction of the focus
            if outcome == OUTCOME_FOCUS_TOO_FAR or self.workspace.memory.egocentric_memory.focus_point is None:
                # If focus TOO FAR or None then turn around
                self.workspace.memory.egocentric_memory.prompt_point = np.array([-100, 0, 0], dtype=int)
            else:
                self.workspace.memory.egocentric_memory.prompt_point = \
                    self.workspace.memory.egocentric_memory.focus_point.copy()
        else:
            self.workspace.memory.egocentric_memory.prompt_point = None

        # Add the enaction to the stack
        return Enaction(self.action, self.workspace.memory)
