########################################################################################
# This decider makes the robot push an object when it has the focus
# Activation 2: when the robot is angry
########################################################################################

# from playsound import playsound
import numpy as np
from pyrr import vector
from . Action import ACTION_TURN, ACTION_FORWARD, ACTION_BACKWARD, ACTION_SCAN
from ..Robot.Enaction import Enaction
from ..Robot.Command import DIRECTION_BACK
from . Decider import Decider
from ..Integrator.OutcomeCode import FOCUS_TOO_FAR_DISTANCE
from .. Enaction.CompositeEnaction import CompositeEnaction
from ..Memory.Memory import EMOTION_ANGRY
from . Interaction import OUTCOME_FLOOR

STEP_INIT = 0
STEP_PUSH = 1


class DeciderPush(Decider):
    def __init__(self, workspace):
        super().__init__(workspace)
        self.too_far = FOCUS_TOO_FAR_DISTANCE
        self.action = self.workspace.actions[ACTION_SCAN]
        self.step = STEP_INIT

    def activation_level(self):
        """The level of activation of this decider: -1: default, 5 if focus inside terrain"""
        activation_level = 0
        if self.workspace.memory.emotion_code == EMOTION_ANGRY:
            activation_level = 4
        # Activate during the withdraw step
        if self.step == STEP_PUSH:
            activation_level = 3  # May return to deciderExplore to return directly to origin
        return activation_level

    def select_enaction(self, outcome):
        """Add the next enaction to the stack based on sequence learning and spatial modifiers"""

        # If there is an object to push
        if self.step == STEP_INIT:
            # Start pushing
            if self.workspace.memory.egocentric_memory.focus_point is not None and outcome != OUTCOME_FLOOR:
                # playsound('autocat/Assets/tiny_cute.wav', False)
                self.workspace.push_sound.play()
                # Compute the prompt
                target_prompt = vector.set_length(self.workspace.memory.egocentric_memory.focus_point, 700)
                self.workspace.memory.egocentric_memory.prompt_point = target_prompt
                # First enaction: turn to the prompt
                e0 = Enaction(self.workspace.actions[ACTION_TURN], self.workspace.memory)
                # Second enaction: move forward to the prompt
                e1 = Enaction(self.workspace.actions[ACTION_FORWARD], e0.predicted_memory)
                composite_enaction = CompositeEnaction([e0, e1])
                self.step = STEP_PUSH
            else:
                # If there is no object then watch (probably never happens)
                print("DeciderPush is watching")
                composite_enaction = Enaction(self.workspace.actions[ACTION_SCAN], self.workspace.memory, span=10)
        else:
            # Start withdrawing
            # The first enaction: turn the back to the prompt
            origin = self.workspace.memory.phenomenon_memory.watch_point()  # Birth place or arena center
            self.workspace.memory.egocentric_memory.prompt_point = self.workspace.memory.allocentric_to_egocentric(origin)
            e0 = Enaction(self.workspace.actions[ACTION_TURN], self.workspace.memory, direction=DIRECTION_BACK)
            # Second enaction: move forward to the prompt
            e1 = Enaction(self.workspace.actions[ACTION_BACKWARD], e0.predicted_memory)
            composite_enaction = CompositeEnaction([e0, e1])
            self.step = STEP_INIT

        return composite_enaction
