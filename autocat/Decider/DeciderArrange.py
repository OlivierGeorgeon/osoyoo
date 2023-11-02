########################################################################################
# This decider makes the robot arrange an object to a specific place
# Activation 2: when the robot is angry
########################################################################################

from playsound import playsound
import numpy as np
from pyrr import vector, line
from . Action import ACTION_SWIPE, ACTION_TURN, ACTION_FORWARD, ACTION_BACKWARD, ACTION_SCAN
from ..Robot.Enaction import Enaction
from . Decider import Decider, FOCUS_TOO_FAR_DISTANCE
from ..Utils import line_intersection
from .. Enaction.CompositeEnaction import CompositeEnaction
from ..Memory.Memory import EMOTION_ANGRY
from . Interaction import OUTCOME_FLOOR
from ..Robot.RobotDefine import TERRAIN_RADIUS


STEP_INIT = 0
STEP_PUSH = 1
STEP_WITHDRAW = 2


class DeciderArrange(Decider):
    def __init__(self, workspace):
        super().__init__(workspace)
        self.too_far = FOCUS_TOO_FAR_DISTANCE
        self.action = self.workspace.actions[ACTION_SCAN]
        self.step = STEP_INIT

    def activation_level(self):
        """The level of activation of this decider: -1: default, 5 if focus inside terrain"""
        activation_level = 0
        if self.workspace.memory.emotional_state() == EMOTION_ANGRY:
            activation_level = 2
        # Activate during the withdraw step
        if self.step in [STEP_PUSH, STEP_WITHDRAW]:
            activation_level = 2
        return activation_level

    def select_enaction(self, outcome):
        """Add the next enaction to the stack based on sequence learning and spatial modifiers"""

        # If there is an object to push
        if self.step == STEP_INIT:
            # Go to position and push
            if self.workspace.memory.egocentric_memory.focus_point is not None and outcome != OUTCOME_FLOOR:
                playsound('autocat/Assets/tiny_cute.wav', False)
                # Compute the prompt: the intersection of the robot's y axis and the object-target line
                l1 = line.create_from_points(self.workspace.memory.egocentric_memory.focus_point,
                                             self.workspace.memory.allocentric_to_egocentric(-np.array(TERRAIN_RADIUS[self.workspace.arena_id])))
                l2 = line.create_from_points([0, 0, 0], [0, 1, 0])
                ego_prompt = line_intersection(l1, l2)
                print("Swiping to align with target by", ego_prompt, "focus", self.workspace.memory.egocentric_memory.focus_point, "target", self.workspace.memory.allocentric_to_egocentric(-np.array(TERRAIN_RADIUS[self.workspace.arena_id])))
                self.workspace.memory.egocentric_memory.prompt_point = ego_prompt
                # First enaction: swipe to the prompt
                e0 = Enaction(self.workspace.actions[ACTION_SWIPE], self.workspace.memory, color=EMOTION_ANGRY)
                # Second enaction: turn toward the focus
                e0.post_memory.egocentric_memory.prompt_point = e0.post_memory.egocentric_memory.focus_point.copy()
                e1 = Enaction(self.workspace.actions[ACTION_TURN], e0.post_memory, color=EMOTION_ANGRY)
                # Third enaction: push toward the target
                target_prompt = e1.post_memory.allocentric_to_egocentric(-np.array(TERRAIN_RADIUS[self.workspace.arena_id]))
                e1.post_memory.egocentric_memory.prompt_point = target_prompt
                e2 = Enaction(self.workspace.actions[ACTION_FORWARD], e1.post_memory, color=EMOTION_ANGRY)
                composite_enaction = CompositeEnaction([e0, e1, e2])
                self.step = STEP_PUSH
            else:
                # If there is no object then watch (probably never append)
                print("DeciderArrange is watching")
                composite_enaction = Enaction(self.workspace.actions[ACTION_SCAN], self.workspace.memory, span=10, color=EMOTION_ANGRY)
        else:
            # Withdraw
            # The first enaction: turn the back to the prompt
            origin = self.workspace.memory.phenomenon_memory.terrain_center()  # Birth place or arena center
            self.workspace.memory.egocentric_memory.prompt_point = self.workspace.memory.allocentric_to_egocentric(origin)
            e0 = Enaction(self.workspace.actions[ACTION_TURN], self.workspace.memory, turn_back=True, color=EMOTION_ANGRY)
            # Second enaction: move forward to the prompt
            e1 = Enaction(self.workspace.actions[ACTION_BACKWARD], e0.post_memory, color=EMOTION_ANGRY)
            composite_enaction = CompositeEnaction([e0, e1])
            self.step = STEP_INIT

        return composite_enaction
