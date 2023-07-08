########################################################################################
# This decider makes the robot circle around an echo object or a territory delimited by a line
# Activation 1: default. 3: focus
########################################################################################

import numpy as np
from . Action import ACTION_TURN
from . Interaction import OUTCOME_DEFAULT
from . PredefinedInteractions import OUTCOME_LOST_FOCUS, OUTCOME_FOCUS_TOO_CLOSE,  OUTCOME_FOCUS_FAR, OUTCOME_FOCUS_SIDE, \
    OUTCOME_FOCUS_FRONT, OUTCOME_FLOOR_LEFT, OUTCOME_FLOOR_FRONT, OUTCOME_FLOOR_RIGHT
from ..Robot.Enaction import Enaction
from . Decider import Decider


class DeciderCircle(Decider):
    def __init__(self, workspace):
        """ Creating our agent """
        super().__init__(workspace)

        # Load the predefined behavior
        # self.procedural_memory = create_interactions(self.workspace.actions)
        # self.action = self.workspace.actions[ACTION_FORWARD]

    def activation_level(self):
        """Return the activation level of this decider/ 1: default; 3 if focus object """
        activation_level = 1

        if self.workspace.memory.egocentric_memory.focus_point is not None:
            if np.linalg.norm(self.workspace.memory.egocentric_memory.focus_point) < 500:
                activation_level = 3
        return activation_level

    def outcome(self, enacted_enaction):
        """ Convert the enacted interaction into an outcome adapted to the circle behavior """
        outcome = OUTCOME_DEFAULT

        # On startup return DEFAULT
        if enacted_enaction is None:
            return outcome

        # If there is a focus point, compute the echo outcome (focus may come from echo or from impact)
        if enacted_enaction.focus_point is not None:
            if np.linalg.norm(enacted_enaction.focus_point) < 200:  # From the center of the robot
                outcome = OUTCOME_FOCUS_TOO_CLOSE
            elif np.linalg.norm(enacted_enaction.focus_point) > 400:  # Must be farther than the forward speed
                outcome = OUTCOME_FOCUS_FAR
            elif enacted_enaction.focus_point[1] > 150:
                outcome = OUTCOME_FOCUS_SIDE  # More that 150 to the left
            elif enacted_enaction.focus_point[1] > 0:
                outcome = OUTCOME_FOCUS_FRONT      # between 0 and 150 to the left
            elif enacted_enaction.focus_point[1] > -150:
                # outcome = OUTCOME_RIGHT     # Between 0 and -150 to the right
                outcome = OUTCOME_FOCUS_FRONT     # Between 0 and -150 to the right
            else:
                # outcome = OUTCOME_FAR_RIGHT  # More that -150 to the right
                outcome = OUTCOME_FOCUS_SIDE

        if enacted_enaction.lost_focus:
            outcome = OUTCOME_LOST_FOCUS

        # If floor then override the focus outcome
        if enacted_enaction.outcome.floor > 0:
            if enacted_enaction.outcome.floor == 0b10:
                outcome = OUTCOME_FLOOR_LEFT
            if enacted_enaction.outcome.floor == 0b11:
                outcome = OUTCOME_FLOOR_FRONT
            if enacted_enaction.outcome.floor == 0b01:
                outcome = OUTCOME_FLOOR_RIGHT

        return outcome

    def select_enaction(self, outcome):
        """Add the next enaction to the stack based on sequence learning and spatial modifiers"""

        # Call the sequence learning mechanism to select the next action
        self.select_action(outcome)

        # Set the spatial modifiers
        if self.action.action_code in [ACTION_TURN]:
            # Turn to the direction of the focus
            self.workspace.memory.egocentric_memory.prompt_point = self.workspace.memory.egocentric_memory.focus_point.copy()
        else:
            self.workspace.memory.egocentric_memory.prompt_point = None

        # Add the enaction to the stack
        self.workspace.enactions[self.workspace.clock] = Enaction(self.action, self.workspace.clock)
