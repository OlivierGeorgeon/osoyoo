########################################################################################
# This decider makes the robot push an object when it has the focus
# Activation 5: when the robot has the focus
########################################################################################

from playsound import playsound
import numpy as np
from pyrr import vector
from . Action import ACTION_WATCH, ACTION_TURN, ACTION_FORWARD, ACTION_BACKWARD, ACTION_SCAN
from ..Robot.Enaction import Enaction
from . Decider import Decider, FOCUS_TOO_FAR_DISTANCE
from .. Enaction.CompositeEnaction import CompositeEnaction
from ..Memory.PhenomenonMemory.PhenomenonMemory import TER
from ..Memory.PhenomenonMemory.PhenomenonTerrain import TERRAIN_ORIGIN_CONFIDENCE
from . Interaction import OUTCOME_FLOOR, OUTCOME_FOCUS_TOO_FAR

STEP_INIT = 0
STEP_PUSH = 1


class DeciderPush(Decider):
    def __init__(self, workspace):
        super().__init__(workspace)
        self.too_far = FOCUS_TOO_FAR_DISTANCE
        self.action = self.workspace.actions[ACTION_SCAN]
        self.step = STEP_INIT

    def activation_level(self):
        """The level of activation of this decider: -1: default, 5 if focus not too far """
        activation_level = -1

        # Push objects only when the terrain has been built
        if TER in self.workspace.memory.phenomenon_memory.phenomena and \
                self.workspace.memory.phenomenon_memory.phenomena[TER].confidence >= TERRAIN_ORIGIN_CONFIDENCE:
            # If there is focus not too far
            # if vector.length(self.workspace.memory.allocentric_memory.robot_point -
            #                  self.workspace.memory.phenomenon_memory.origin_point()) < 400 \
            #         and self.workspace.memory.egocentric_memory.focus_point is not None \
            #         and vector.length(self.workspace.memory.egocentric_memory.focus_point) < FOCUS_TOO_FAR_DISTANCE:
            #     activation_level = 5
            # If the focus is inside the terrain

            allo_focus = self.workspace.memory.egocentric_to_allocentric(self.workspace.memory.egocentric_memory.focus_point)
            if self.workspace.memory.phenomenon_memory.phenomena[TER].is_inside(allo_focus):
                activation_level = 5
            else:
                print("Focus outside terrain", self.workspace.memory.egocentric_memory.focus_point)

        # Activate during the withdraw step
        if self.step == STEP_PUSH:
            activation_level = 5

        return activation_level

    def select_enaction(self, outcome):
        """Add the next enaction to the stack based on sequence learning and spatial modifiers"""

        # If there is an object to push
        if self.step == STEP_INIT:
            # Start pushing
            if self.workspace.memory.egocentric_memory.focus_point is not None and outcome != OUTCOME_FLOOR:
                playsound('autocat/Assets/tiny_cute.wav', False)
                # Compute the prompt
                target_prompt = vector.set_length(self.workspace.memory.egocentric_memory.focus_point, 700)
                self.workspace.memory.egocentric_memory.prompt_point = target_prompt
                # First enaction: turn to the prompt
                e0 = Enaction(self.workspace.actions[ACTION_TURN], self.workspace.memory, color=4)
                # Second enaction: move forward to the prompt
                e1 = Enaction(self.workspace.actions[ACTION_FORWARD], e0.post_memory, color=4)
                # Third enaction: move back to the origin
                # origin = e1.post_memory.phenomenon_memory.origin_point()  # Birth place or arena center
                # e1.post_memory.egocentric_memory.prompt_point = e1.post_memory.allocentric_to_egocentric(origin)
                # print("Return to center, egocentric position", e1.post_memory.egocentric_memory.prompt_point)
                # e2 = Enaction(self.workspace.actions[ACTION_BACKWARD], e1.post_memory)
                # composite_enaction = CompositeEnaction([e0, e1, e2])
                composite_enaction = CompositeEnaction([e0, e1])
                self.step = STEP_PUSH
            else:
                # If there is no object then watch
                print("Push decider is watching")
                composite_enaction = Enaction(self.workspace.actions[ACTION_SCAN], self.workspace.memory, span=10, color=4)
        elif self.step == STEP_PUSH:
            # Start withdrawing
            # The first enaction: turn the back to the prompt
            origin = self.workspace.memory.phenomenon_memory.terrain_center()  # Birth place or arena center
            self.workspace.memory.egocentric_memory.prompt_point = self.workspace.memory.allocentric_to_egocentric(origin)
            e0 = Enaction(self.workspace.actions[ACTION_TURN], self.workspace.memory, turn_back=True, color=4)
            # Second enaction: move forward to the prompt
            e1 = Enaction(self.workspace.actions[ACTION_BACKWARD], e0.post_memory, color=4)
            composite_enaction = CompositeEnaction([e0, e1])
            self.step = STEP_INIT

        return composite_enaction
