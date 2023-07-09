########################################################################################
# This decider makes the robot stay in place and look at objects in its surrounding
# Activation 4: default.
########################################################################################

import math
import numpy as np
from . Action import ACTION_WATCH, ACTION_TURN, ACTION_SWIPE, ACTION_FORWARD
from . Interaction import Interaction, OUTCOME_DEFAULT
from . PredefinedInteractions import OUTCOME_FOCUS_TOO_FAR, OUTCOME_LOST_FOCUS, OUTCOME_FOCUS_SIDE, OUTCOME_FOCUS_FRONT
from ..Robot.Enaction import Enaction
from . Decider import Decider, FOCUS_TOO_FAR_DISTANCE, FOCUS_SIDE_ANGLE


class DeciderWatch(Decider):
    def __init__(self, workspace):
        super().__init__(workspace)

        # Give higher valence to Watch than to Swipe
        # TODO handle switching between deciders
        Interaction.create_or_retrieve(workspace.actions[ACTION_SWIPE], OUTCOME_DEFAULT, 1)
        Interaction.create_or_retrieve(workspace.actions[ACTION_FORWARD], OUTCOME_DEFAULT, 1)
        Interaction.create_or_retrieve(workspace.actions[ACTION_WATCH], OUTCOME_DEFAULT, 2)

        self.action = self.workspace.actions[ACTION_WATCH]

    def activation_level(self):
        """The level of activation of this decider: 0: default, 2 if the terrain has an origin """
        return 4

    def outcome(self, enacted_enaction):
        """ Convert the enacted interaction into an outcome adapted to the watch behavior """

        # On startup
        if enacted_enaction is None:
            return OUTCOME_FOCUS_FRONT

        outcome = OUTCOME_FOCUS_FRONT

        if enacted_enaction.focus_point is None:
            # If there is no focus then consider it was lost and trigger scan
            outcome = OUTCOME_LOST_FOCUS
        else:
            if np.linalg.norm(enacted_enaction.focus_point) > FOCUS_TOO_FAR_DISTANCE:
                outcome = OUTCOME_FOCUS_TOO_FAR
            else:
                angle = math.atan2(enacted_enaction.focus_point[1], enacted_enaction.focus_point[0])
                if math.fabs(angle) > FOCUS_SIDE_ANGLE:
                    outcome = OUTCOME_FOCUS_SIDE

        # DEFAULT when focused on object in near front
        return outcome

    def select_enaction(self, outcome):
        """Return the next intended interaction"""

        # Call the sequence learning mechanism to select the next action
        self.select_action(outcome)

        # Set the spatial modifiers
        if self.action.action_code in [ACTION_TURN]:
            if outcome == OUTCOME_FOCUS_TOO_FAR or self.workspace.memory.egocentric_memory.focus_point is None:
                # If focus TOO FAR or None then turn around
                self.workspace.memory.egocentric_memory.prompt_point = np.array([-100, 0, 0], dtype=int)
            else:
                # If focus SIDE then turn to the focus
                self.workspace.memory.egocentric_memory.prompt_point = \
                    self.workspace.memory.egocentric_memory.focus_point.copy()
        else:
            self.workspace.memory.egocentric_memory.prompt_point = None

        # Add the enaction to the stack
        self.workspace.enactions[self.workspace.clock] = Enaction(self.action, self.workspace.clock)
