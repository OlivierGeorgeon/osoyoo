########################################################################################
# This proposer makes the robot play by turning around a DOT phenomenon
# EMOTION_CONTENT (Serotonin) when playing
# EMOTION_VIGILANCE (Noradrenaline) when searching
########################################################################################

import math
import numpy as np
from . Action import ACTION_TURN, ACTION_FORWARD, ACTION_SWIPE
from ..Robot.Enaction import Enaction
from . Proposer import Proposer
from ..Memory import EMOTION_CONTENT, EMOTION_VIGILANCE
from ..Memory.EgocentricMemory.Experience import EXPERIENCE_FLOOR
from ..Memory.AllocentricMemory.AllocentricMemory import CLOCK_PLACE
from ..Enaction.CompositeEnaction import CompositeEnaction
from ..Robot.RobotDefine import ROBOT_FLOOR_SENSOR_X
from ..Memory.AllocentricMemory.Geometry import point_to_cell
from ..Proposer.Interaction import OUTCOME_LOST_FOCUS, OUTCOME_FLOOR

PLAY_DISTANCE_CLOSE = 200  # Between robot center and object center
PLAY_DISTANCE_WITHDRAW = 250  # From where the robot has stopped


class ProposerPlayDot(Proposer):
    def __init__(self, workspace):
        super().__init__(workspace)
        self.last_seen_focus = None
        self.emotion = EMOTION_CONTENT

    def activation_level(self):
        """The level of activation of this decider: Serotonin level + 1  """
        return self.workspace.memory.body_memory.serotonin # + 51

    def propose_enaction(self):
        """Add the next enaction to the stack based on sequence learning and spatial modifiers"""

        enaction = self.workspace.enaction
        if enaction is None:
            return None

        # If no DOT phenomenon then no proposition
        p_id = self.workspace.memory.phenomenon_memory.focus_phenomenon_id
        if p_id is None:
            return None

        e_memory = self.workspace.memory.save()
        # If lost the phenomenon then move the focus to the side
        if enaction.outcome_code == OUTCOME_FLOOR:
            self.emotion = EMOTION_CONTENT
            self.last_seen_focus = None
        elif enaction.outcome_code == OUTCOME_LOST_FOCUS or self.emotion == EMOTION_VIGILANCE:
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
                e_memory.egocentric_memory.focus_point = left_of_focus
            else:
                e_memory.egocentric_memory.focus_point = right_of_focus
                # focus = self.workspace.memory.egocentric_memory.focus_point + np.array([0, -80, 0])
            # e_memory.egocentric_memory.focus_point = focus
            self.emotion = EMOTION_VIGILANCE

        # If focus at a dot phenomenon
        e_memory.emotion_code = self.emotion
        p = self.workspace.memory.phenomenon_memory.phenomena[p_id]
        if p.phenomenon_type == EXPERIENCE_FLOOR:
            # If very playful and the dot is forward
            if self.workspace.memory.body_memory.serotonin > 55 and \
                    e_memory.egocentric_memory.focus_point[0] > ROBOT_FLOOR_SENSOR_X:
                if abs(e_memory.egocentric_memory.focus_point[1]) < 20:
                    # If in front then go to the dot
                    e_memory.egocentric_memory.prompt_point = None  # e_memory.egocentric_memory.focus_point.copy()   # Don't stop at the dot
                    return Enaction(self.workspace.actions[ACTION_FORWARD], e_memory)
                elif abs(math.degrees(math.atan2(e_memory.egocentric_memory.focus_point[1],
                                                 e_memory.egocentric_memory.focus_point[0]))) < 15:
                    # If slightly in front then swipe
                    e_memory.egocentric_memory.prompt_point = e_memory.egocentric_memory.focus_point.copy()
                    return Enaction(self.workspace.actions[ACTION_SWIPE], e_memory)
                else:
                    # If not in front then turn
                    e_memory.egocentric_memory.prompt_point = e_memory.egocentric_memory.focus_point.copy()
                    return Enaction(self.workspace.actions[ACTION_TURN], e_memory)

            # If mildly playful then turn around the dot
            if e_memory.egocentric_memory.focus_point[0] > ROBOT_FLOOR_SENSOR_X:
                # First enaction SWIPE in the direction of the focus
                if e_memory.egocentric_memory.focus_point[1] > 0:
                    e_memory.egocentric_memory.prompt_point = None
                else:
                    e_memory.egocentric_memory.prompt_point = np.array([0, -200, 0])
                e0 = Enaction(self.workspace.actions[ACTION_SWIPE], e_memory)
                # Second enaction TURN to focus
                e0.predicted_memory.egocentric_memory.prompt_point = e0.predicted_memory.egocentric_memory.focus_point.copy()
                e1 = Enaction(self.workspace.actions[ACTION_TURN], e0.predicted_memory)
                # Third enaction move FORWARD to focus
                e1.predicted_memory.egocentric_memory.prompt_point = None  # Don't stop at the dot
                e2 = Enaction(self.workspace.actions[ACTION_FORWARD], e1.predicted_memory)
                return CompositeEnaction([e0, e1, e2])
            else:
                # First enaction TURN to focus
                e_memory.egocentric_memory.prompt_point = e_memory.egocentric_memory.focus_point.copy()
                e0 = Enaction(self.workspace.actions[ACTION_TURN], e_memory)
                # Second enaction move FORWARD to focus
                e0.predicted_memory.egocentric_memory.prompt_point = None  # Don't stop at the dot
                e1 = Enaction(self.workspace.actions[ACTION_FORWARD], e0.predicted_memory)
                return CompositeEnaction([e0, e1])
