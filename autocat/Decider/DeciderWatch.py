########################################################################################
# This decider makes the robot stay in place and look at objects in its surrounding
# Activation 4: default.
########################################################################################

import math
import numpy as np
from . Action import ACTION_WATCH, ACTION_TURN, ACTION_SWIPE
from . Interaction import Interaction
from . PredefinedInteractions import OUTCOME_FOCUS_TOO_FAR, OUTCOME_LOST_FOCUS, OUTCOME_FOCUS_SIDE, OUTCOME_FOCUS_FRONT
from ..Robot.Enaction import Enaction
from . Decider import Decider


class DeciderWatch(Decider):
    def __init__(self, workspace):
        super().__init__(workspace)

        # Give higher valence to Watch than to Swipe
        # TODO handle switching between deciders
        Interaction.create_or_retrieve(workspace.actions[ACTION_SWIPE], OUTCOME_FOCUS_FRONT, 1)
        Interaction.create_or_retrieve(workspace.actions[ACTION_WATCH], OUTCOME_FOCUS_FRONT, 2)

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
            if np.linalg.norm(enacted_enaction.focus_point) > 600:
                outcome = OUTCOME_FOCUS_TOO_FAR
            else:
                angle = math.atan2(enacted_enaction.focus_point[1], enacted_enaction.focus_point[0])
                if math.fabs(angle) > math.pi / 6:
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
                # If focus then turn to the focus
                self.workspace.memory.egocentric_memory.prompt_point = \
                    self.workspace.memory.egocentric_memory.focus_point.copy()
        else:
            self.workspace.memory.egocentric_memory.prompt_point = None

        # Add the enaction to the stack
        self.workspace.enactions[self.workspace.clock] = Enaction(self.action, self.workspace.clock)

        # # Recording previous interaction
        # self.previous_interaction = self.last_interaction
        # self.last_interaction = Interaction.create_or_retrieve(self.action, outcome)
        #
        # # Tracing the last interaction
        # if self.action is not None:
        #     print("Action: " + str(self.action) +
        #           ", Anticipation: " + str(self.anticipated_outcome) +
        #           ", Outcome: " + str(outcome) +
        #           ", Satisfaction: (anticipation: " + str(self.anticipated_outcome == outcome) +
        #           ", valence: " + str(self.last_interaction.valence) + ")")
        #
        # self.workspace.memory.egocentric_memory.prompt_point = None
        # # If focus FAR: Turn around or Scan - (idem circle)
        # if outcome == OUTCOME_FOCUS_TOO_FAR:
        #     if self.action.action_code == ACTION_TURN:
        #         self.action = self.workspace.actions[ACTION_SCAN]
        #     else:
        #         self.workspace.memory.egocentric_memory.focus_point = None  # Prepare to catch focus again
        #         self.workspace.memory.egocentric_memory.prompt_point = np.array([-100, 0, 0], dtype=int)
        #         self.action = self.workspace.actions[ACTION_TURN]
        # # No Focus: Scan - (idem circle)
        # elif outcome == OUTCOME_LOST_FOCUS:
        #     self.action = self.workspace.actions[ACTION_SCAN]
        #     self.workspace.memory.egocentric_memory.prompt_point = None
        # # Focussed on an object on the side: Align towards it - (idem circle)
        # elif outcome == OUTCOME_FOCUS_SIDE:
        #     self.workspace.memory.egocentric_memory.prompt_point = self.workspace.memory.egocentric_memory.focus_point.copy()
        #     self.action = self.workspace.actions[ACTION_TURN]
        # # Focus is NEARBY: Keep watching
        # else:
        #     self.action = self.workspace.actions[ACTION_WATCH]
        #     self.workspace.memory.egocentric_memory.prompt_point = None
        #
        # self.workspace.enactions[self.workspace.clock] = Enaction(self.action, self.workspace.clock)
