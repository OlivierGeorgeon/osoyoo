########################################################################################
# The attention mechanism may select another focus
########################################################################################

import numpy as np
from ..Memory.AllocentricMemory.AllocentricMemory import CLOCK_PLACE
from ..Memory.AllocentricMemory.Geometry import point_to_cell
from ..Proposer.Interaction import OUTCOME_LOST_FOCUS, OUTCOME_FLOOR
from ..Memory.BodyMemory import NORADRENALINE


class AttentionMechanism:
    def __init__(self, workspace):
        self.workspace = workspace
        self.last_seen_focus = None

    def update_focus(self):
        """If the dot point has been lost, select another focus"""

        enaction = self.workspace.enaction
        if enaction is None:
            return

        # If no DOT phenomenon then don't change focus
        p_id = self.workspace.memory.phenomenon_memory.focus_phenomenon_id
        if p_id is None:
            return

        # If the dot was found again then
        if enaction.outcome_code == OUTCOME_FLOOR:
            self.workspace.memory.body_memory.neurotransmitters[NORADRENALINE] = 50
            self.last_seen_focus = None

        # If lost the phenomenon then move the focus to the side
        elif enaction.outcome_code == OUTCOME_LOST_FOCUS or self.workspace.memory.body_memory.neurotransmitters[NORADRENALINE] > 50:
            if self.last_seen_focus is None:
                # Memorise the allocentric last seen focus for the next try
                self.last_seen_focus = self.workspace.memory.egocentric_to_allocentric(self.workspace.memory.egocentric_memory.focus_point)
            else:
                # Reuse the last seen focus
                self.workspace.memory.egocentric_memory.focus_point = self.workspace.memory.allocentric_to_egocentric(self.last_seen_focus)
            left_of_focus = self.workspace.memory.egocentric_memory.focus_point + np.array([0, 80, 0])
            i, j = point_to_cell(self.workspace.memory.egocentric_to_allocentric(left_of_focus))
            last_visited_left = self.workspace.memory.allocentric_memory.grid[i, j, CLOCK_PLACE]
            right_of_focus = self.workspace.memory.egocentric_memory.focus_point + np.array([0, -80, 0])
            i, j = point_to_cell(self.workspace.memory.egocentric_to_allocentric(right_of_focus))
            last_visited_right = self.workspace.memory.allocentric_memory.grid[i, j, CLOCK_PLACE]
            print(f"Searching left {last_visited_left}, right {last_visited_right}")
            if last_visited_left < last_visited_right:
                # focus = self.workspace.memory.egocentric_memory.focus_point + np.array([0, 80, 0])
                self.workspace.memory.egocentric_memory.focus_point = left_of_focus
            else:
                self.workspace.memory.egocentric_memory.focus_point = right_of_focus
                # focus = self.workspace.memory.egocentric_memory.focus_point + np.array([0, -80, 0])
            self.workspace.memory.body_memory.neurotransmitters[NORADRENALINE] = 60
