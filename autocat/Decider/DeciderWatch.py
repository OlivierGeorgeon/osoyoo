########################################################################################
# This decider makes the robot stay in place and look at objects in its surrounding
# Activation 4: default.
########################################################################################

from . Interaction import Interaction, OUTCOME_DEFAULT
from . Action import ACTION_WATCH, ACTION_TURN
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

        outcome = OUTCOME_DEFAULT

        return outcome

    def intended_enaction(self, outcome):
        """Return the next intended interaction"""
        # Tracing the last interaction
        if self._action is not None:
            print("Action: " + str(self._action) + ", Anticipation: " + str(self.anticipated_outcome) +
                  ", Outcome: " + str(outcome))

        self._action = self.workspace.actions[ACTION_WATCH]

        # Compute the next prompt point
        return Enaction(self._action, self.workspace.clock, self.workspace.memory)
