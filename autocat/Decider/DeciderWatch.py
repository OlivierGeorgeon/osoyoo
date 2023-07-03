########################################################################################
# This decider makes the robot stay in place and look at objects in its surrounding
# Activation 4: default.
########################################################################################

import math
import numpy as np
from . Interaction import Interaction, OUTCOME_DEFAULT
from . PredefinedInteractions import OUTCOME_FAR_FRONT, OUTCOME_LOST_FOCUS, OUTCOME_FAR_LEFT
from . Action import ACTION_WATCH, ACTION_SCAN, ACTION_TURN
from ..Robot.Enaction import Enaction

# OUTCOME_SIDE = 'S'
# OUTCOME_NO_FOCUS = 'N'


class DeciderWatch:
    def __init__(self, workspace):
        self.workspace = workspace
        self.anticipated_outcome = OUTCOME_DEFAULT
        self.previous_interaction = None
        self.last_interaction = None
        self._action = self.workspace.actions[ACTION_WATCH]

    def activation_level(self):
        """The level of activation of this decider: 0: default, 2 if the terrain has an origin """
        return 4

    def propose_intended_enaction(self, enacted_enaction):
        """Propose the next intended enaction from the previous enacted interaction.
        This is the main method of the agent"""
        # Compute a specific outcome suited for this agent
        outcome = self.outcome(enacted_enaction)
        # Compute the intended enaction
        return self.intended_enaction(outcome)

    def outcome(self, enacted_enaction):
        """ Convert the enacted interaction into an outcome adapted to the watch behavior """

        # On startup
        if enacted_enaction is None:
            return OUTCOME_DEFAULT

        outcome = OUTCOME_DEFAULT

        if enacted_enaction.focus_point is None:
            # If there is no focus then consider it was lost and trigger scan
            outcome = OUTCOME_LOST_FOCUS
        else:
            if np.linalg.norm(enacted_enaction.focus_point) > 600:
                outcome = OUTCOME_FAR_FRONT
            else:
                angle = math.atan2(enacted_enaction.focus_point[1], enacted_enaction.focus_point[0])
                if math.fabs(angle) > math.pi / 6:
                    outcome = OUTCOME_FAR_LEFT

        return outcome

    def intended_enaction(self, outcome):
        """Return the next intended interaction"""
        # Tracing the last interaction

        # Recording previous interaction
        self.previous_interaction = self.last_interaction
        self.last_interaction = Interaction.create_or_retrieve(self._action, outcome)

        # Tracing the last interaction
        if self._action is not None:
            print("Action: " + str(self._action) +
                  ", Anticipation: " + str(self.anticipated_outcome) +
                  ", Outcome: " + str(outcome) +
                  ", Satisfaction: (anticipation: " + str(self.anticipated_outcome == outcome) +
                  ", valence: " + str(self.last_interaction.valence) + ")")

        self.workspace.memory.egocentric_memory.prompt_point = None
        # If focus FAR: Turn around or Scan
        if outcome == OUTCOME_FAR_FRONT:
            if self._action.action_code == ACTION_TURN:
                self._action = self.workspace.actions[ACTION_SCAN]
            else:
                self.workspace.memory.egocentric_memory.focus_point = None  # Prepare to catch focus again
                self.workspace.memory.egocentric_memory.prompt_point = np.array([-100, 0, 0], dtype=int)
                self._action = self.workspace.actions[ACTION_TURN]
        # No Focus: Scan
        elif outcome == OUTCOME_LOST_FOCUS:
            self._action = self.workspace.actions[ACTION_SCAN]
            self.workspace.memory.egocentric_memory.prompt_point = None
        # Focussed on an object on the side: Align towards it
        elif outcome == OUTCOME_FAR_LEFT:
            self.workspace.memory.egocentric_memory.prompt_point = self.workspace.memory.egocentric_memory.focus_point.copy()
            self._action = self.workspace.actions[ACTION_TURN]
        # DEFAULT: Keep watching
        else:
            self._action = self.workspace.actions[ACTION_WATCH]
            self.workspace.memory.egocentric_memory.prompt_point = None

        return Enaction(self._action, self.workspace.clock, self.workspace.memory)
