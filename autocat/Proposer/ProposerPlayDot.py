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
from ..Memory.BodyMemory import SEROTONIN
from ..Proposer.Interaction import OUTCOME_ANY
from ..Proposer.PredefinedInteractions import create_or_retrieve_primitive, create_primitive_interactions

PLAY_DISTANCE_CLOSE = 200  # Between robot center and object center
PLAY_DISTANCE_WITHDRAW = 250  # From where the robot has stopped


class ProposerPlayDot(Proposer):
    # def __init__(self, workspace):
    #     super().__init__(workspace)
    #     self.last_seen_focus = None
    #     self.emotion = EMOTION_CONTENT

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
        # If focus at a dot phenomenon
        # e_memory.emotion_code = self.emotion
        p = self.workspace.memory.phenomenon_memory.phenomena[p_id]
        if p.phenomenon_type == EXPERIENCE_FLOOR:
            # If very playful and the dot is forward
            if self.workspace.memory.body_memory.neurotransmitters[SEROTONIN] > 55 and \
                    e_memory.egocentric_memory.focus_point[0] > ROBOT_FLOOR_SENSOR_X:
                if abs(e_memory.egocentric_memory.focus_point[1]) < 20:
                    # If in front then go to the dot
                    e_memory.egocentric_memory.prompt_point = None  # e_memory.egocentric_memory.focus_point.copy()   # Don't stop at the dot
                    i0 = create_or_retrieve_primitive(self.workspace.primitive_interactions, self.workspace.actions[ACTION_FORWARD], OUTCOME_FLOOR)
                    e0 = Enaction(i0, e_memory)
                    return CompositeEnaction([e0], "Play DOT", np.array([0, 1, 0]))
                elif abs(math.degrees(math.atan2(e_memory.egocentric_memory.focus_point[1],
                                                 e_memory.egocentric_memory.focus_point[0]))) < 15:
                    # If slightly in front then swipe
                    e_memory.egocentric_memory.prompt_point = e_memory.egocentric_memory.focus_point.copy()
                    i0 = create_or_retrieve_primitive(self.workspace.primitive_interactions, self.workspace.actions[ACTION_SWIPE], OUTCOME_ANY)
                    e0 = Enaction(i0, e_memory)
                    return CompositeEnaction([e0], "Play DOT", np.array([0, 1, 0]))
                else:
                    # If not in front then turn
                    e_memory.egocentric_memory.prompt_point = e_memory.egocentric_memory.focus_point.copy()
                    i0 = create_or_retrieve_primitive(self.workspace.primitive_interactions, self.workspace.actions[ACTION_TURN], OUTCOME_ANY)
                    e = Enaction(i0, e_memory)
                    return CompositeEnaction([e], "Play DOT", np.array([0, 1, 0]))

            # If mildly playful then turn around the dot
            if e_memory.egocentric_memory.focus_point[0] > ROBOT_FLOOR_SENSOR_X:
                # First enaction SWIPE in the direction of the focus
                if e_memory.egocentric_memory.focus_point[1] > 0:
                    e_memory.egocentric_memory.prompt_point = None
                else:
                    e_memory.egocentric_memory.prompt_point = np.array([0, -200, 0])
                i0 = create_or_retrieve_primitive(self.workspace.primitive_interactions, self.workspace.actions[ACTION_SWIPE], OUTCOME_ANY)
                e0 = Enaction(i0, e_memory)
                # Second enaction TURN to focus
                e0.predicted_memory.egocentric_memory.prompt_point = e0.predicted_memory.egocentric_memory.focus_point.copy()
                i1 = create_or_retrieve_primitive(self.workspace.primitive_interactions, self.workspace.actions[ACTION_TURN], OUTCOME_ANY)
                e1 = Enaction(i1, e0.predicted_memory)
                # Third enaction move FORWARD to focus
                e1.predicted_memory.egocentric_memory.prompt_point = None  # Don't stop at the dot
                i2 = create_or_retrieve_primitive(self.workspace.primitive_interactions, self.workspace.actions[ACTION_FORWARD], OUTCOME_ANY)
                e2 = Enaction(i2, e1.predicted_memory)
                return CompositeEnaction([e0, e1, e2], "Play DOT", np.array([0, 1, 0]))
            else:
                # First enaction TURN to focus
                e_memory.egocentric_memory.prompt_point = e_memory.egocentric_memory.focus_point.copy()
                i0 = create_or_retrieve_primitive(self.workspace.primitive_interactions, self.workspace.actions[ACTION_TURN], OUTCOME_ANY)
                e0 = Enaction(i0, e_memory)
                # Second enaction move FORWARD to focus
                e0.predicted_memory.egocentric_memory.prompt_point = None  # Don't stop at the dot
                i1 = create_or_retrieve_primitive(self.workspace.primitive_interactions, self.workspace.actions[ACTION_FORWARD], OUTCOME_ANY)
                e1 = Enaction(i1, e0.predicted_memory)
                return CompositeEnaction([e0, e1], "Play DOT", np.array([0, 1, 0]))
