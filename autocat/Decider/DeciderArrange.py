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

        # If OUTCOME_FLOOR just scan
        if outcome == OUTCOME_FLOOR:
            self.step = STEP_INIT
            return Enaction(self.workspace.actions[ACTION_SCAN], self.workspace.memory, span=10, color=EMOTION_UPSET)

        ego_target = self.workspace.memory.terrain_centric_to_egocentric(
            -np.array(TERRAIN_RADIUS[self.workspace.arena_id]))

        # If object behind target just watch
        if ego_target[0] < self.workspace.memory.egocentric_memory.focus_point[0]:
            self.step = STEP_INIT  # Prevents being stuck
            print("object behind target")
            return Enaction(self.workspace.actions[ACTION_WATCH], self.workspace.memory, color=EMOTION_UPSET)

        # If STEP_INIT
        if self.step == STEP_INIT:
            l1 = line.create_from_points(self.workspace.memory.egocentric_memory.focus_point, ego_target)
            l2 = line.create_from_points([0, 0, 0], [0, 1, 0])
            ego_prompt = line_intersection(l1, l2)
            # test = point_closest_point_on_line(np.array([0, 0, 0], l1))
            # If robot_point_object-target not aligned
            if math.fabs(ego_prompt[1]) > 50:
                # swipe to intersection
                allo_prompt = self.workspace.memory.egocentric_to_allocentric(ego_prompt)
                # If prompt inside the terrain
                if self.workspace.memory.phenomenon_memory.phenomena[TER].is_inside(allo_prompt):
                    print("Swiping to align with target by", ego_prompt, "focus",
                          self.workspace.memory.egocentric_memory.focus_point, "target",
                          self.workspace.memory.terrain_centric_to_egocentric(
                              -np.array(TERRAIN_RADIUS[self.workspace.arena_id])))
                    self.workspace.memory.egocentric_memory.prompt_point = ego_prompt
                    # Swipe to the prompt
                    composite_enaction = Enaction(self.workspace.actions[ACTION_SWIPE], self.workspace.memory,
                                                  color=EMOTION_ANGRY)
                # If prompt outside the terrain
                else:
                    # Just scan again
                    composite_enaction = Enaction(self.workspace.actions[ACTION_SCAN], self.workspace.memory,
                                                  color=EMOTION_ANGRY)
            # If robot_point-object-target are aligned
            else:
                # If robot_direction also aligned
                self.workspace.memory.egocentric_memory.prompt_point = ego_target
                if math.fabs(math.atan2(ego_target[1], ego_target[0])) < math.radians(10):
                    # Push to target
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

        # If there is an object to push
        # if self.step == STEP_INIT:
        #     # Go to position
        #     if self.workspace.memory.egocentric_memory.focus_point is not None and outcome != OUTCOME_FLOOR:
        #         # Compute the prompt: the intersection of the robot's y axis and the object-target line
        #         ego_target = self.workspace.memory.terrain_centric_to_egocentric(-np.array(TERRAIN_RADIUS[self.workspace.arena_id]))
        #         if ego_target[0] > self.workspace.memory.egocentric_memory.focus_point[0]:
        #             # The object is closer than the target
        #             playsound('autocat/Assets/tiny_cute.wav', False)
        #             l1 = line.create_from_points(self.workspace.memory.egocentric_memory.focus_point, ego_target)
        #             l2 = line.create_from_points([0, 0, 0], [0, 1, 0])
        #             ego_prompt = line_intersection(l1, l2)
        #             if math.fabs(ego_prompt[1]) > 50:
        #                 # Swipe to align with the target
        #                 print("Swiping to align with target by", ego_prompt, "focus", self.workspace.memory.egocentric_memory.focus_point, "target", self.workspace.memory.terrain_centric_to_egocentric(-np.array(TERRAIN_RADIUS[self.workspace.arena_id])))
        #                 self.workspace.memory.egocentric_memory.prompt_point = ego_prompt
        #                 # First enaction: swipe to the prompt
        #                 e0 = Enaction(self.workspace.actions[ACTION_SWIPE], self.workspace.memory, color=EMOTION_ANGRY)
        #                 # Second enaction: turn toward the target
        #                 # e0.post_memory.egocentric_memory.prompt_point = e0.post_memory.egocentric_memory.focus_point.copy()
        #                 e0.post_memory.egocentric_memory.prompt_point = e0.post_memory.terrain_centric_to_egocentric(-np.array(TERRAIN_RADIUS[self.workspace.arena_id]))
        #                 e1 = Enaction(self.workspace.actions[ACTION_TURN], e0.post_memory, color=EMOTION_ANGRY)
        #                 # Third enaction: push toward the target
        #                 # target_prompt = e1.post_memory.terrain_centric_to_egocentric(-np.array(TERRAIN_RADIUS[self.workspace.arena_id]))
        #                 # e1.post_memory.egocentric_memory.prompt_point = target_prompt
        #                 # e2 = Enaction(self.workspace.actions[ACTION_FORWARD], e1.post_memory, color=EMOTION_ANGRY)
        #                 # composite_enaction = CompositeEnaction([e0, e1, e2])
        #             else:
        #                 # Just turn toward the target
        #                 self.workspace.memory.egocentric_memory.prompt_point = ego_target
        #                 e0 = Enaction(self.workspace.actions[ACTION_TURN], self.workspace.memory, color=EMOTION_ANGRY)
        #                 composite_enaction = CompositeEnaction([e0])
        #             self.step = STEP_PUSH
        #         else:
        #             # If the object is farther than the target, the robot stays put and is upset
        #             print("UPSET, focus", self.workspace.memory.egocentric_memory.focus_point, "target", self.workspace.memory.terrain_centric_to_egocentric(-np.array(TERRAIN_RADIUS[self.workspace.arena_id])))
        #             playsound('autocat/Assets/tiny_cute2.wav', False)
        #             composite_enaction = Enaction(self.workspace.actions[ACTION_WATCH], self.workspace.memory, span=10, color=EMOTION_UPSET)
        #     else:
        #         # If there is no object then watch (probably never append)
        #         print("DeciderArrange is watching")
        #         composite_enaction = Enaction(self.workspace.actions[ACTION_SCAN], self.workspace.memory, span=10, color=EMOTION_ANGRY)
        # else:
        #     # Withdraw
        #     # The first enaction: turn the back to the prompt
        #     origin = self.workspace.memory.phenomenon_memory.terrain_center()  # Birth place or arena center
        #     self.workspace.memory.egocentric_memory.prompt_point = self.workspace.memory.allocentric_to_egocentric(origin)
        #     e0 = Enaction(self.workspace.actions[ACTION_TURN], self.workspace.memory, turn_back=True, color=EMOTION_ANGRY)
        #     # Second enaction: move forward to the prompt
        #     e1 = Enaction(self.workspace.actions[ACTION_BACKWARD], e0.post_memory, color=EMOTION_ANGRY)
        #     composite_enaction = CompositeEnaction([e0, e1])
        #     self.step = STEP_INIT
        #
        # return composite_enaction
