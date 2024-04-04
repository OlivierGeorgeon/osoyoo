########################################################################################
# Propose to play by going back and forth from the center of the terrain to the border
# Activation 0: default. 3: the terrain has an absolute reference
# EMOTION_CONTENT (Serotonin)
########################################################################################

import math
import numpy as np
from pyrr import quaternion, Quaternion, Vector3
from . Action import ACTION_TURN, ACTION_FORWARD, ACTION_BACKWARD
from . Proposer import Proposer
from ..Robot.Command import DIRECTION_BACK
from ..Robot.Enaction import Enaction
from ..Memory.PhenomenonMemory import PHENOMENON_CLOSED_CONFIDENCE
from ..Memory import EMOTION_CONTENT
from ..Enaction.CompositeEnaction import CompositeEnaction
from . GoalGenerator import GoalGenerator


class ProposerPlayTerrain(Proposer):
    def __init__(self, workspace):
        super().__init__(workspace)
        # The goal generator proposes successive goal points to explore the terrain
        self.goal_generator = GoalGenerator(workspace)

    def activation_level(self):
        """The level of activation is 3 if serotonin"""

        return self.workspace.memory.body_memory.serotonin

        if self.workspace.memory.body_memory.serotonin >= 50:
            return 4
        return 0

    def select_enaction(self, enaction):
        """Propose the next enaction"""

        # If the terrain is not closed, don't play with it
        if self.workspace.memory.phenomenon_memory.terrain_confidence() < PHENOMENON_CLOSED_CONFIDENCE:
            return None

        e_memory = self.workspace.memory.save()
        e_memory.emotion_code = EMOTION_CONTENT

        # If the robot is at the center of the terrain
        if np.linalg.norm(self.workspace.memory.terrain_centric_robot_point()) < 200:
            # Got to a new goal on the border of the terrain
            ego_prompt = self.workspace.memory.terrain_centric_to_egocentric(self.goal_generator.terrain_goal_point())
            e_memory.egocentric_memory.prompt_point = ego_prompt
            e_memory.egocentric_memory.focus_point = None  # Prevent unnatural head movement
            e1 = Enaction(self.workspace.actions[ACTION_TURN], e_memory)
            e2 = Enaction(self.workspace.actions[ACTION_FORWARD], e1.predicted_memory.save())
            return CompositeEnaction([e1, e2])

        # Withdraw step
        else:
            ego_watch_point = self.workspace.memory.terrain_centric_to_egocentric(np.array([0, 0, 0]))
            e_memory.egocentric_memory.prompt_point = ego_watch_point
            # First enaction: re-align the back toward the watch point
            e1 = Enaction(self.workspace.actions[ACTION_TURN], e_memory, direction=DIRECTION_BACK)
            # Second enaction: move back to the prompt
            e2 = Enaction(self.workspace.actions[ACTION_BACKWARD], e1.predicted_memory.save())
            return CompositeEnaction([e1, e2])
