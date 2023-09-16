########################################################################################
# This decider makes the robot push an object when it has the focus
# Activation 5: when the robot has the focus
########################################################################################

from playsound import playsound
import numpy as np
from pyrr import vector
from . Action import ACTION_WATCH, ACTION_TURN, ACTION_FORWARD, ACTION_BACKWARD
from ..Robot.Enaction import Enaction
from . Decider import Decider, FOCUS_TOO_FAR_DISTANCE
from . PredefinedInteractions import OUTCOME_FOCUS_TOO_FAR
from .. Enaction.CompositeEnaction import CompositeEnaction
from ..Memory.PhenomenonMemory.PhenomenonMemory import TER
from ..Memory.PhenomenonMemory.PhenomenonTerrain import TERRAIN_INITIAL_CONFIDENCE

STEP_INIT = 0
STEP_PUSH = 1


class DeciderPush(Decider):
    def __init__(self, workspace):
        super().__init__(workspace)
        self.too_far = FOCUS_TOO_FAR_DISTANCE
        self.action = self.workspace.actions[ACTION_WATCH]
        self.step = STEP_INIT

    def activation_level(self):
        """The level of activation of this decider: -1: default, 5 if focus not too far """
        activation_level = -1

        # Push objects only when the terrain has been built
        if TER in self.workspace.memory.phenomenon_memory.phenomena and \
                self.workspace.memory.phenomenon_memory.phenomena[TER].confidence > TERRAIN_INITIAL_CONFIDENCE + 0.01:
            # If there is focus not too far
            if vector.length(self.workspace.memory.allocentric_memory.robot_point -
                             self.workspace.memory.phenomenon_memory.origin_point()) < 400 \
                    and self.workspace.memory.egocentric_memory.focus_point is not None \
                    and vector.length(self.workspace.memory.egocentric_memory.focus_point) < FOCUS_TOO_FAR_DISTANCE:
                activation_level = 5

        # Activate during the withdraw step
        if self.step == STEP_PUSH:
            activation_level = 5

        return activation_level

    def select_enaction(self, outcome):
        """Add the next enaction to the stack based on sequence learning and spatial modifiers"""

        # If there is an object to push
        if self.step == STEP_INIT:
            # Start pushing
            if self.workspace.memory.egocentric_memory.focus_point is not None and outcome != OUTCOME_FOCUS_TOO_FAR:
                playsound('autocat/Assets/tiny_cute.wav', False)
                # Compute the prompt
                target_prompt = vector.set_length(self.workspace.memory.egocentric_memory.focus_point, 700)
                self.workspace.memory.egocentric_memory.prompt_point = target_prompt
                # First enaction: turn to the prompt
                e0 = Enaction(self.workspace.actions[ACTION_TURN], self.workspace.memory)
                # Second enaction: move forward to the prompt
                e1 = Enaction(self.workspace.actions[ACTION_FORWARD], e0.post_memory)
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
                composite_enaction = Enaction(self.workspace.actions[ACTION_WATCH], self.workspace.memory)
        elif self.step == STEP_PUSH:
            # Start withdrawing
            # The first enaction: turn the back to the prompt
            origin = self.workspace.memory.phenomenon_memory.origin_point()  # Birth place or arena center
            self.workspace.memory.egocentric_memory.prompt_point = self.workspace.memory.allocentric_to_egocentric(origin)
            e0 = Enaction(self.workspace.actions[ACTION_TURN], self.workspace.memory, turn_back=True)
            # Second enaction: move forward to the prompt
            e1 = Enaction(self.workspace.actions[ACTION_BACKWARD], e0.post_memory)
            composite_enaction = CompositeEnaction([e0, e1])
            self.step = STEP_INIT

        return composite_enaction
