########################################################################################
# This decider makes the robot circle around an echo object or a territory delimited by a line
# Activation 1: default. 3: focus
########################################################################################

import math
import numpy as np
from . Action import ACTION_TURN
from . Interaction import OUTCOME_NO_FOCUS
from . PredefinedInteractions import OUTCOME_LOST_FOCUS, OUTCOME_FOCUS_TOO_CLOSE,  OUTCOME_FOCUS_FAR, OUTCOME_FOCUS_SIDE, \
    OUTCOME_FOCUS_FRONT, OUTCOME_FLOOR, OUTCOME_FOCUS_TOO_FAR
from ..Robot.Enaction import Enaction
from . Decider import Decider, FOCUS_TOO_CLOSE_DISTANCE, FOCUS_FAR_DISTANCE, FOCUS_TOO_FAR_DISTANCE, FOCUS_SIDE_ANGLE


class DeciderCircle(Decider):
    def __init__(self, workspace):
        """ Creating our agent """
        super().__init__(workspace)

    def activation_level(self):
        """Return the activation level of this decider/ 1: default; 3 if focus not too far """
        activation_level = 1

        # Activate when the focus is not too far
        if self.workspace.memory.egocentric_memory.focus_point is not None:
            if np.linalg.norm(self.workspace.memory.egocentric_memory.focus_point) < FOCUS_TOO_FAR_DISTANCE:
                activation_level = 3

        return activation_level

    # def outcome(self, enacted_enaction):
    #     """ Convert the enacted interaction into an outcome adapted to the circle behavior """
    #     outcome = OUTCOME_NO_FOCUS
    #
    #     # On startup return DEFAULT
    #     if enacted_enaction is None:
    #         return outcome
    #
    #     # If there is a focus point, compute the echo outcome (focus may come from echo or from impact)
    #     if enacted_enaction.focus_point is not None:
    #         focus_radius = np.linalg.norm(enacted_enaction.focus_point)  # From the center of the robot
    #         if focus_radius < FOCUS_TOO_CLOSE_DISTANCE:
    #             outcome = OUTCOME_FOCUS_TOO_CLOSE
    #         elif focus_radius > FOCUS_TOO_FAR_DISTANCE:
    #             outcome = OUTCOME_FOCUS_TOO_FAR
    #         elif focus_radius > FOCUS_FAR_DISTANCE:
    #             outcome = OUTCOME_FOCUS_FAR
    #         else:
    #             focus_theta = math.atan2(enacted_enaction.focus_point[1], enacted_enaction.focus_point[0])
    #             if math.fabs(focus_theta) < FOCUS_SIDE_ANGLE:
    #                 outcome = OUTCOME_FOCUS_FRONT
    #             else:
    #                 outcome = OUTCOME_FOCUS_SIDE
    #
    #     if enacted_enaction.lost_focus:
    #         outcome = OUTCOME_LOST_FOCUS
    #
    #     # If floor then override the focus outcome
    #     if enacted_enaction.outcome.floor > 0:
    #         outcome = OUTCOME_FLOOR
    #
    #     return outcome

    def select_enaction(self, outcome):
        """Add the next enaction to the stack based on sequence learning and spatial modifiers"""

        # Call the sequence learning mechanism to select the next action
        self.select_action(outcome)

        # Set the spatial modifiers
        if self.action.action_code in [ACTION_TURN]:
            # Turn to the direction of the focus
            self.workspace.memory.egocentric_memory.prompt_point = \
                self.workspace.memory.egocentric_memory.focus_point.copy()
        else:
            self.workspace.memory.egocentric_memory.prompt_point = None

        # Add the enaction to the stack
        self.workspace.enactions[self.workspace.clock] = Enaction(self.action, self.workspace.clock)
