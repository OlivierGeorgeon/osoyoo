########################################################################################
# This decider makes the robot arrange an object to a specific place
# Activation 2: when the robot is angry
########################################################################################
import math

from playsound import playsound
import numpy as np
from pyrr import vector, line, Quaternion
from pyrr.geometric_tests import point_closest_point_on_line
from . Action import ACTION_SWIPE, ACTION_TURN, ACTION_FORWARD, ACTION_BACKWARD, ACTION_SCAN, ACTION_WATCH
from ..Robot.Enaction import Enaction
from ..Robot.Command import DIRECTION_LEFT, DIRECTION_RIGHT
from . Decider import Decider, FOCUS_TOO_FAR_DISTANCE
from ..Utils import line_intersection
from .. Enaction.CompositeEnaction import CompositeEnaction
from ..Memory.Memory import EMOTION_ANGRY, EMOTION_UPSET
from ..Memory.PhenomenonMemory.PhenomenonMemory import TER
from . Interaction import OUTCOME_FLOOR
from ..Robot.RobotDefine import TERRAIN_RADIUS


STEP_INIT = 0
STEP_PUSH = 1


class DeciderArrange(Decider):
    def __init__(self, workspace):
        super().__init__(workspace)
        self.too_far = FOCUS_TOO_FAR_DISTANCE
        self.action = self.workspace.actions[ACTION_SCAN]
        self.step = STEP_INIT

    def activation_level(self):
        """The level of activation of this decider: 0: default, 4 if angry, and then 3."""
        activation_level = 0
        # Activation 4 when angry: the highest of all deciders
        if self.workspace.memory.emotion_code == EMOTION_ANGRY:
            activation_level = 4
        # Activation 3 during the withdraw step, same as DeciderExplore
        if self.step == STEP_PUSH:
            activation_level = 3
        return activation_level

    def select_enaction(self, outcome):
        """The enactions to push a object to a target place"""

        # If STEP_INIT
        if self.step == STEP_INIT:
            ego_target = self.workspace.memory.terrain_centric_to_egocentric(
                -np.array(TERRAIN_RADIUS[self.workspace.arena_id]))
            # If OUTCOME_FLOOR just scan
            if outcome == OUTCOME_FLOOR:
                self.step = STEP_INIT
                composite_enaction = Enaction(self.workspace.actions[ACTION_SCAN], self.workspace.memory, span=10,
                                              color=EMOTION_UPSET)
            # If object behind target just watch
            elif ego_target[0] < self.workspace.memory.egocentric_memory.focus_point[0]:
                print("object behind target")
                composite_enaction = Enaction(self.workspace.actions[ACTION_WATCH], self.workspace.memory,
                                              color=EMOTION_UPSET)
            # If object to push
            else:
                l1 = line.create_from_points(self.workspace.memory.egocentric_memory.focus_point, ego_target)
                ego_prompt_intersection = line_intersection(l1, line.create_from_points([0, 0, 0], [0, 1, 0]))
                ego_prompt_projection = point_closest_point_on_line(np.array([0, 0, 0]), l1)
                print("Prompt projection:", ego_prompt_projection, "focus:",
                      self.workspace.memory.egocentric_memory.focus_point, "target:", ego_target)
                # If robot_point_object-target not aligned
                if math.fabs(ego_prompt_projection[1]) > 50:
                    # Go to the point from where to push
                    allo_prompt = self.workspace.memory.egocentric_to_allocentric(ego_prompt_projection)
                    # If angle to projection point greater than 20°
                    # if self.workspace.memory.phenomenon_memory.phenomena[TER].is_inside(allo_prompt):
                    if math.fabs(math.atan2(ego_prompt_projection[0], math.fabs(ego_prompt_projection[1]))) > 0.349:
                        self.workspace.memory.egocentric_memory.prompt_point = ego_prompt_projection
                        # Turn the left to the projection
                        if ego_prompt_projection[1] > 0:
                            # Turn the left to the prompt
                            e0 = Enaction(self.workspace.actions[ACTION_TURN], self.workspace.memory,
                                          direction=DIRECTION_LEFT, color=EMOTION_ANGRY)
                        else:
                            # Turn the right to the prompt
                            e0 = Enaction(self.workspace.actions[ACTION_TURN], self.workspace.memory,
                                          direction=DIRECTION_RIGHT, color=EMOTION_ANGRY)
                        # Swipe to the prompt
                        e1 = Enaction(self.workspace.actions[ACTION_SWIPE], e0.post_memory, color=EMOTION_ANGRY)
                        composite_enaction = CompositeEnaction([e0, e1])
                    # If angle lawer than 20°
                    else:
                        print("Swipe to intersection", ego_prompt_intersection)
                        self.workspace.memory.egocentric_memory.prompt_point = ego_prompt_intersection
                        composite_enaction = Enaction(self.workspace.actions[ACTION_SWIPE], self.workspace.memory,
                                                      color=EMOTION_ANGRY)
                    # If prompt outside the terrain
                    # else:
                    #     # Just scan again
                    #     composite_enaction = Enaction(self.workspace.actions[ACTION_SCAN], self.workspace.memory,
                    #                                   color=EMOTION_ANGRY)
                # If robot_point-object-target are aligned
                else:
                    # If robot_direction also aligned by less than 20°
                    self.workspace.memory.egocentric_memory.prompt_point = ego_target
                    if math.fabs(math.atan2(ego_target[1], ego_target[0])) < 0.349:
                        # Push to target
                        self.workspace.memory.egocentric_memory.focus_point = ego_target.copy()  # Look at the destination
                        composite_enaction = Enaction(self.workspace.actions[ACTION_FORWARD], self.workspace.memory,
                                                      color=EMOTION_ANGRY)
                        self.step = STEP_PUSH
                    # If robot_direction not aligned
                    else:
                        # Turn to target
                        composite_enaction = Enaction(self.workspace.actions[ACTION_TURN], self.workspace.memory,
                                                      color=EMOTION_ANGRY)
        # If STEP_PUSH
        else:
            # Slight Withdraw
            self.workspace.memory.egocentric_memory.prompt_point = None
            composite_enaction = Enaction(self.workspace.actions[ACTION_BACKWARD], self.workspace.memory,
                                          color=EMOTION_ANGRY)
            self.step = STEP_INIT

        return composite_enaction
