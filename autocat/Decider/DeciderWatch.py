########################################################################################
# This decider makes the robot stay in place and look at objects in its surrounding
# Activation 4: default.
########################################################################################

import math
from . Interaction import Interaction, OUTCOME_DEFAULT
from . PredefinedInteractions import OUTCOME_LOST_FOCUS, OUTCOME_LEFT
from . Action import ACTION_WATCH, ACTION_SCAN, ACTION_TURN
from ..Robot.Enaction import Enaction


class DeciderWatch:
    def __init__(self, workspace):
        self.workspace = workspace
        self.anticipated_outcome = OUTCOME_DEFAULT
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
            if enacted_enaction.status == 'lost':
                outcome = OUTCOME_LOST_FOCUS
            else:
                enacted_enaction.focus_point = enacted_enaction.echo_point
                self.workspace.memory.egocentric_memory.focus_point = enacted_enaction.focus_point

        if enacted_enaction.focus_point is not None:
            angle = math.atan2(enacted_enaction.focus_point[1], enacted_enaction.focus_point[0])
            if math.fabs(angle) > math.pi / 6:
                outcome = OUTCOME_LEFT

        return outcome

    def intended_enaction(self, outcome):
        """Return the next intended interaction"""
        # Tracing the last interaction
        if self._action is not None:
            print("Action: " + str(self._action) + ", Anticipation: " + str(self.anticipated_outcome) +
                  ", Outcome: " + str(outcome))

        if outcome == OUTCOME_DEFAULT:
            self._action = self.workspace.actions[ACTION_WATCH]
            self.workspace.memory.egocentric_memory.prompt_point = None
        elif outcome == OUTCOME_LOST_FOCUS:
            self._action = self.workspace.actions[ACTION_SCAN]
            self.workspace.memory.egocentric_memory.prompt_point = None
        else:
            self.workspace.memory.egocentric_memory.prompt_point = self.workspace.memory.egocentric_memory.focus_point.copy()
            self._action = self.workspace.actions[ACTION_TURN]

        # Compute the next prompt point
        return Enaction(self._action, self.workspace.clock, self.workspace.memory)
