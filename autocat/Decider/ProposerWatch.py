########################################################################################
# This decider makes the robot stay at the watch point and watch for objects in its surrounding
# And also listen for messages from the other robot
# This behavior is associated with EMOTION_SAD
########################################################################################

import math
import numpy as np
from . Action import ACTION_TURN, ACTION_FORWARD, ACTION_SCAN
from ..Robot.Enaction import Enaction
from ..Memory import EMOTION_SAD
from ..Enaction.CompositeEnaction import CompositeEnaction
from . Proposer import Proposer
from . PredefinedInteractions import OUTCOME_FOCUS_SIDE
from ..Memory.BodyMemory import ENERGY_TIRED, EXCITATION_LOW
from ..Memory.PhenomenonMemory.PhenomenonTerrain import TERRAIN_ORIGIN_CONFIDENCE
from ..Memory.PhenomenonMemory import ARRANGE_OBJECT_RADIUS

STEP_INIT = 0
STEP_TURN = 1


class ProposerWatch(Proposer):
    def __init__(self, workspace):
        super().__init__(workspace)
        self.step = STEP_INIT

    def activation_level(self):
        """The level of activation is 2 if terrain is confident and no object to arrange"""
        if self.workspace.memory.phenomenon_memory.terrain_confidence() >= TERRAIN_ORIGIN_CONFIDENCE and \
                self.workspace.memory.body_memory.energy >= ENERGY_TIRED and \
                self.workspace.memory.body_memory.excitation <= EXCITATION_LOW:
            return 2
            # if self.workspace.memory.egocentric_memory.focus_point is None:
            #     return 2
            # else:
            #     ego_target = self.workspace.memory.terrain_centric_to_egocentric(self.workspace.memory.phenomenon_memory.arrange_point())
            #     is_to_arrange = self.workspace.memory.is_to_arrange(self.workspace.memory.egocentric_memory.focus_point)
            #     is_closer = self.workspace.memory.egocentric_memory.focus_point[0] < ego_target[0] - ARRANGE_OBJECT_RADIUS
            #     print("Focus near terrain center:", is_to_arrange, ". Before terrain center:", is_closer,
            #           ". Other robot angry:", self.workspace.memory.phenomenon_memory.other_robot_is_angry())
            #     if not is_to_arrange:
            #         return 2
        return 0

    def outcome(self, enaction):
        """ Convert the enacted interaction into an outcome adapted to the watch behavior """

        outcome = super().outcome(enaction)

        # If a message was received then we focus on the other robot
        if enaction is not None and enaction.message is not None:
            other_angle = math.atan2(enaction.message.ego_position[1], enaction.message.ego_position[0])
            if math.fabs(other_angle) > math.pi / 6:
                # Focus on the other robot's destination
                print("Other ego destination point", enaction.message.ego_position)
                print("Other angle", math.degrees(other_angle))
                self.workspace.memory.egocentric_memory.focus_point = enaction.message.ego_position
                outcome = OUTCOME_FOCUS_SIDE
        return outcome

    def select_enaction(self, enaction):
        """Return the next intended interaction"""

        e_memory = self.workspace.memory.save()
        e_memory.emotion_code = EMOTION_SAD
        ego_watch_point = self.workspace.memory.terrain_centric_to_egocentric(np.array([0, 0, 0]))

        # If far from watch point then go to watch point
        if np.linalg.norm(ego_watch_point) > 200:
            e_memory.egocentric_memory.prompt_point = ego_watch_point
            # e_memory.egocentric_memory.focus_point = None  # Prevent unnatural head movement
            # First enaction: turn to the prompt
            e0 = Enaction(self.workspace.actions[ACTION_TURN], e_memory)
            # Second enaction: move forward to the prompt
            e1 = Enaction(self.workspace.actions[ACTION_FORWARD], e0.predicted_memory.save())
            self.step = STEP_INIT
            return CompositeEnaction([e0, e1])

        # If at watch point and STEP_INIT then scan
        elif self.step == STEP_INIT:
            self.step = STEP_TURN
            return Enaction(self.workspace.actions[ACTION_SCAN], e_memory, span=10)

        # If at watch point and STEP_TURN then turn
        else:
            self.step = STEP_INIT
            e_memory.egocentric_memory.prompt_point = np.array([-1200, 1, 0], dtype=int)
            e_memory.egocentric_memory.focus_point = np.array([-1200, 1, 0], dtype=int)
            return Enaction(self.workspace.actions[ACTION_TURN], e_memory)
