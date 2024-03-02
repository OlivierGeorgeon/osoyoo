########################################################################################
# This decider makes the robot stay in the watch point and watch for objects in its surrounding
# And also listen for messages from the other robot
# Activation 2 if emotion is SAD
########################################################################################

import math
import numpy as np
from . Action import ACTION_WATCH, ACTION_TURN, ACTION_SWIPE, ACTION_FORWARD, ACTION_SCAN
from ..Robot.Enaction import Enaction
from ..Memory.Memory import EMOTION_SAD
from ..Enaction.CompositeEnaction import CompositeEnaction
from . Proposer import Proposer
from . PredefinedInteractions import create_or_retrieve_primitive, OUTCOME_FOCUS_SIDE, OUTCOME_FOCUS_FRONT, \
    OUTCOME_FOCUS_TOO_FAR
from ..Memory.BodyMemory import ENERGY_TIRED, EXCITATION_LOW
from ..Memory.PhenomenonMemory.PhenomenonTerrain import TERRAIN_ORIGIN_CONFIDENCE
from ..Memory.PhenomenonMemory import ARRANGE_OBJECT_RADIUS

STEP_INIT = 0
STEP_TURN = 1


class ProposerWatch(Proposer):
    def __init__(self, workspace):
        super().__init__(workspace)
        self.step = STEP_INIT

        # Give higher valence to Watch than to Swipe
        # create_or_retrieve_primitive(self.primitive_interactions, workspace.actions[ACTION_SWIPE], OUTCOME_FOCUS_FRONT, 1)
        # create_or_retrieve_primitive(self.primitive_interactions, workspace.actions[ACTION_FORWARD], OUTCOME_FOCUS_FRONT, 1)
        # create_or_retrieve_primitive(self.primitive_interactions, workspace.actions[ACTION_WATCH], OUTCOME_FOCUS_FRONT, 2)

        # Beyond this threshold, the robot ignores the echo and keep scanning and turning 180° in search for echos
        # self.too_far = FOCUS_FAR_DISTANCE  # Good for active watching for new objects to push

        # self.action = self.workspace.actions[ACTION_WATCH]

    def activation_level(self):
        """The level of activation is 2 if the robot is SAD"""
        if self.workspace.memory.phenomenon_memory.terrain_confidence() >= TERRAIN_ORIGIN_CONFIDENCE:
            # High energy then must circle, explore, watch or arrange
            if self.workspace.memory.body_memory.energy >= ENERGY_TIRED:
                # High excitation then must circle or explore
                if self.workspace.memory.body_memory.excitation <= EXCITATION_LOW:
                    # High energy with low excitation, must watch or arrange
                    # if self.is_outside_terrain(self.egocentric_memory.focus_point):
                    if self.workspace.memory.egocentric_memory.focus_point is None:
                        return 2
                    else:
                        # If object in the area where it must be arranged
                        ego_target = self.workspace.memory.terrain_centric_to_egocentric(self.workspace.memory.phenomenon_memory.arrange_point())
                        is_to_arrange = self.workspace.memory.is_to_arrange(self.workspace.memory.egocentric_memory.focus_point)
                        # print("Ego focus", self.egocentric_memory.focus_point)
                        # if object is closer than target point (minus the radius to prevent keeping pushing)
                        is_closer = self.workspace.memory.egocentric_memory.focus_point[0] < ego_target[0] - ARRANGE_OBJECT_RADIUS
                        print("Focus near terrain center:", is_to_arrange, ". Before terrain center:", is_closer,
                              ". Other robot angry:", self.workspace.memory.phenomenon_memory.other_robot_is_angry())
                        if not is_to_arrange:
                            return 2
        # if self.workspace.memory.emotion_code == EMOTION_SAD:
        #     return 2
        # else:
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
                # self.workspace.message_sound.play()
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
            # Third enaction: scan
            # e2 = Enaction(self.workspace.actions[ACTION_SCAN], e1.predicted_memory.save(), span=10)
            self.step = STEP_INIT
            return CompositeEnaction([e0, e1])  #, e2])  # Scan because it often miss an object

        # If at watch point and INIT then scan
        elif self.step == STEP_INIT:
            self.step = STEP_TURN
            return Enaction(self.workspace.actions[ACTION_SCAN], e_memory, span=10)
        else:
            self.step = STEP_INIT
            e_memory.egocentric_memory.prompt_point = np.array([-1200, 1, 0], dtype=int)
            e_memory.egocentric_memory.focus_point = np.array([-1200, 1, 0], dtype=int)
            return Enaction(self.workspace.actions[ACTION_TURN], e_memory)

        # # Call the sequence learning mechanism to select the next action
        # self.select_action(enaction)
        # span = 40
        #
        # # Set the spatial modifiers
        # if self.action.action_code in [ACTION_TURN]:
        #     if enaction.outcome_code == OUTCOME_FOCUS_TOO_FAR or e_memory.egocentric_memory.focus_point is None:
        #         # If focus TOO FAR or None then turn around
        #         e_memory.egocentric_memory.prompt_point = np.array([-100, 0, 0], dtype=int)
        #     else:
        #         # If focus SIDE then turn to the focus
        #         e_memory.egocentric_memory.prompt_point = e_memory.egocentric_memory.focus_point.copy()
        # else:
        #     e_memory.egocentric_memory.prompt_point = None
        #     if self.action.action_code in [ACTION_SCAN]:
        #         # Watch carefully
        #         span = 10
        #
        # # Return the selected enaction
        # return Enaction(self.action, e_memory, span=span)
