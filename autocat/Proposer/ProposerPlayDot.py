########################################################################################
# This proposer makes the robot play by turning around a DOT phenomenon
# EMOTION_CONTENT (Serotonin)
########################################################################################
import math

import numpy as np
from . Action import ACTION_TURN, ACTION_FORWARD, ACTION_SWIPE, ACTION_BACKWARD
from ..Robot.Enaction import Enaction
from . Proposer import Proposer
from ..Memory import EMOTION_CONTENT
from ..Memory.EgocentricMemory.Experience import EXPERIENCE_FLOOR
from ..Enaction.CompositeEnaction import CompositeEnaction
from ..Robot.RobotDefine import ROBOT_FLOOR_SENSOR_X

STEP_INIT = 0
STEP_WITHDRAW = 1

PLAY_DISTANCE_CLOSE = 200  # Between robot center and object center
PLAY_DISTANCE_WITHDRAW = 250  # From where the robot has stopped


class ProposerPlayDot(Proposer):

    def activation_level(self):
        """The level of activation of this decider: Serotonin level + 1  """
        return self.workspace.memory.body_memory.serotonin + 51

    def select_enaction(self, enaction):
        """Add the next enaction to the stack based on sequence learning and spatial modifiers"""

        p_id = self.workspace.memory.phenomenon_memory.focus_phenomenon_id
        # If no focus then no proposition
        if p_id is None:
            return None

        # If focus at a dot phenomenon
        p = self.workspace.memory.phenomenon_memory.phenomena[p_id]
        if p.phenomenon_type == EXPERIENCE_FLOOR:
            e_memory = self.workspace.memory.save()
            e_memory.emotion_code = EMOTION_CONTENT
            # If in front then forward
            if e_memory.egocentric_memory.focus_point[0] > ROBOT_FLOOR_SENSOR_X \
                    and abs(e_memory.egocentric_memory.focus_point[1]) < 10:
                e_memory.egocentric_memory.prompt_point = e_memory.egocentric_memory.focus_point.copy()
                e = Enaction(self.workspace.actions[ACTION_FORWARD], e_memory)
            # If behind then turn
            elif e_memory.egocentric_memory.focus_point[0] < -ROBOT_FLOOR_SENSOR_X:
                e_memory.egocentric_memory.prompt_point = e_memory.egocentric_memory.focus_point.copy()
                e = Enaction(self.workspace.actions[ACTION_TURN], e_memory)
            # If underneath  the robot then backward
            elif -ROBOT_FLOOR_SENSOR_X <= e_memory.egocentric_memory.focus_point[0] <= ROBOT_FLOOR_SENSOR_X:
                e_memory.egocentric_memory.prompt_point = np.array([-300, 0, 0])
                e = Enaction(self.workspace.actions[ACTION_BACKWARD], e_memory)
            elif np.linalg.norm(e_memory.egocentric_memory.focus_point) > 300:
                e_memory.egocentric_memory.prompt_point = e_memory.egocentric_memory.focus_point.copy()
                if abs(math.atan2(e_memory.egocentric_memory.focus_point[1], e_memory.egocentric_memory.focus_point[0]) > math.radians(15)):
                    e = Enaction(self.workspace.actions[ACTION_TURN], e_memory)
                else:
                    e = Enaction(self.workspace.actions[ACTION_SWIPE], e_memory)
            # If left then swipe left
            elif e_memory.egocentric_memory.focus_point[1] > 0:
                e_memory.egocentric_memory.prompt_point = None
                e = Enaction(self.workspace.actions[ACTION_SWIPE], e_memory)
            # If right then swipe right
            else:
                e_memory.egocentric_memory.prompt_point = np.array([0, -300, 0])
                e = Enaction(self.workspace.actions[ACTION_SWIPE], e_memory)
            return e

            # First enaction SWIPE
            e_memory.egocentric_memory.prompt_point = None
            e0 = Enaction(self.workspace.actions[ACTION_SWIPE], e_memory)
            # Second enaction TURN to focus
            e0.predicted_memory.egocentric_memory.prompt_point = e0.predicted_memory.egocentric_memory.focus_point.copy()
            e1 = Enaction(self.workspace.actions[ACTION_TURN], e0.predicted_memory)
            # Third enaction move FORWARD to focus
            e2 = Enaction(self.workspace.actions[ACTION_FORWARD], e1.predicted_memory)
            return CompositeEnaction([e0, e1, e2])
