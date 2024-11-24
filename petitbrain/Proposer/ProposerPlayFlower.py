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
from ..Memory.EgocentricMemory.Experience import EXPERIENCE_FLOOR
from ..Enaction.CompositeEnaction import CompositeEnaction
from ..Robot.RobotDefine import ROBOT_FLOOR_SENSOR_X
from ..Proposer.Interaction import OUTCOME_PROMPT, OUTCOME_FLOOR, OUTCOME_FOCUS_FRONT
from ..Memory.BodyMemory import SEROTONIN
# from ..Proposer.PredefinedInteractions import create_or_retrieve_primitive, create_primitive_interactions

PLAY_DISTANCE_CLOSE = 200  # Between robot center and object center
PLAY_DISTANCE_WITHDRAW = 250  # From where the robot has stopped
VERY_PLAYFUL = 55  # Above this threshold play forward


class ProposerPlayFlower(Proposer):

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
        p = self.workspace.memory.phenomenon_memory.phenomena[p_id]
        if p.phenomenon_type == EXPERIENCE_FLOOR:
            # If very playful and the dot is forward
            if self.workspace.memory.body_memory.neurotransmitters[SEROTONIN] > VERY_PLAYFUL and \
                    e_memory.egocentric_memory.focus_point[0] > ROBOT_FLOOR_SENSOR_X:
                if abs(e_memory.egocentric_memory.focus_point[1]) < 20:
                    # If in front then go to the dot
                    i0 = self.workspace.primitive_interactions[(ACTION_FORWARD, OUTCOME_FLOOR)]
                    # e_memory.egocentric_memory.prompt_point = None
                    # e0 = Enaction(i0, e_memory)
                    return CompositeEnaction(None, "Play DOT", np.array([0, 1, 0]), [i0], e_memory)
                    # return CompositeEnaction([e0], "Play DOT", np.array([0, 1, 0]))
                elif abs(math.degrees(math.atan2(e_memory.egocentric_memory.focus_point[1],
                                                 e_memory.egocentric_memory.focus_point[0]))) < 15:
                    # If slightly in front then swipe
                    i0 = self.workspace.primitive_interactions[(ACTION_SWIPE, OUTCOME_FOCUS_FRONT)]
                    # e_memory.egocentric_memory.prompt_point = e_memory.egocentric_memory.focus_point.copy()
                    # e0 = Enaction(i0, e_memory)
                    # return CompositeEnaction([e0], "Play DOT", np.array([0, 1, 0]))
                    return CompositeEnaction(None, "Play DOT", np.array([0, 1, 0]), [i0], e_memory)
                else:
                    # If not in front then turn
                    i0 = self.workspace.primitive_interactions[(ACTION_TURN, OUTCOME_FOCUS_FRONT)]
                    # e_memory.egocentric_memory.prompt_point = e_memory.egocentric_memory.focus_point.copy()
                    # e = Enaction(i0, e_memory)
                    # return CompositeEnaction([e], "Play DOT", np.array([0, 1, 0]))
                    return CompositeEnaction(None, "Play DOT", np.array([0, 1, 0]), [i0], e_memory)

            # If mildly playful then turn around the dot
            if e_memory.egocentric_memory.focus_point[0] > ROBOT_FLOOR_SENSOR_X:
                # First enaction SWIPE in the direction of the focus
                if e_memory.egocentric_memory.focus_point[1] > 0:
                    e_memory.egocentric_memory.prompt_point = None
                else:
                    e_memory.egocentric_memory.prompt_point = np.array([0, -200, 0])
                # i0 = self.workspace.primitive_interactions[(ACTION_SWIPE, OUTCOME_PROMPT)]
                # i1 = self.workspace.primitive_interactions[(ACTION_TURN, OUTCOME_FOCUS_FRONT)]
                # i2 = self.workspace.primitive_interactions[(ACTION_FORWARD, OUTCOME_FLOOR)]
                # return CompositeEnaction(None, "Play DOT", np.array([0, 1, 0]), [i0, i1, i2], e_memory)
                return CompositeEnaction(None, "Play DOT", np.array([0, 1, 0]),
                                         self.workspace.sequence_interactions["STF"], e_memory)
            else:
                # # First enaction TURN to focus
                # i0 = self.workspace.primitive_interactions[(ACTION_TURN, OUTCOME_FOCUS_FRONT)]
                # # Second enaction move FORWARD to focus
                # i1 = self.workspace.primitive_interactions[(ACTION_FORWARD, OUTCOME_FLOOR)]
                # return CompositeEnaction(None, "Play DOT", np.array([0, 1, 0]), [i0, i1], e_memory)
                return CompositeEnaction(None, "Play DOT", np.array([0, 1, 0]),
                                         self.workspace.sequence_interactions["TF"], e_memory)
