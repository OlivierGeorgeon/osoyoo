########################################################################################
# This decider makes the robot explore the parts of the terrain that are not yet known
########################################################################################

import numpy as np
from . Action import ACTION_ALIGN_ROBOT, ACTION_FORWARD
from . Interaction import Interaction, OUTCOME_DEFAULT
from ..Robot.Enaction import Enaction

EXPLORATION_STEP_INIT = 0
EXPLORATION_STEP_ROTATE = 1
EXPLORATION_STEP_TRANSLATE = 2


class DeciderExplore:
    def __init__(self, workspace):
        self.workspace = workspace
        self.anticipated_outcome = OUTCOME_DEFAULT

        self.exploration_step = EXPLORATION_STEP_INIT
        self.prompt_point = np.array([-900, 600, 0])

    def propose_intended_enaction(self, enacted_interaction):
        """Propose the next intended enaction from the previous enacted interaction.
        This is the main method of the agent"""
        # Compute a specific outcome suited for this agent
        outcome = self.outcome(enacted_interaction)
        # Compute the intended enaction
        return self.intended_enaction(outcome)

    def outcome(self, enacted_interaction):
        """ Convert the enacted interaction into an outcome adapted to the explore behavior """
        return OUTCOME_DEFAULT

    def intended_enaction(self, outcome):
        """Return the next intended interaction"""
        # Compute the next prompt point
        if self.exploration_step == EXPLORATION_STEP_INIT:
            # Go back and forth
            # self.workspace.memory.egocentric_memory.prompt_point = self.prompt_point.copy()
            self.workspace.memory.egocentric_memory.prompt_point = \
                self.workspace.memory.allocentric_to_egocentric(self.workspace.memory.allocentric_memory.most_interesting_pool())
            self.exploration_step = EXPLORATION_STEP_ROTATE

        # Compute the next intended interaction
        if self.exploration_step == EXPLORATION_STEP_TRANSLATE:
            action = self.workspace.actions[ACTION_FORWARD]
            self.exploration_step = EXPLORATION_STEP_INIT
        if self.exploration_step == EXPLORATION_STEP_ROTATE:
            action = self.workspace.actions[ACTION_ALIGN_ROBOT]
            self.exploration_step = EXPLORATION_STEP_TRANSLATE
        ii = Interaction.create_or_retrieve(action, self.anticipated_outcome)

        return Enaction(ii, self.workspace.clock, self.workspace.memory.egocentric_memory.focus_point,
                        self.workspace.memory.egocentric_memory.prompt_point)
