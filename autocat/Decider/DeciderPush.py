########################################################################################
# This decider makes the robot push an object when it has the focus
# Activation 5: when the robot has the focus
########################################################################################

from playsound import playsound
import numpy as np
from . Action import ACTION_WATCH, ACTION_TURN, ACTION_FORWARD, ACTION_BACKWARD
from ..Robot.Enaction import Enaction
from . Decider import Decider, FOCUS_TOO_FAR_DISTANCE
from . PredefinedInteractions import create_or_retrieve_primitive, OUTCOME_FOCUS_TOO_FAR
from .. Enaction.CompositeEnaction import CompositeEnaction
from ..Memory.PhenomenonMemory.PhenomenonMemory import TER
from ..Memory.PhenomenonMemory.PhenomenonTerrain import TERRAIN_INITIAL_CONFIDENCE


class DeciderPush(Decider):
    def __init__(self, workspace):
        super().__init__(workspace)

        # Give higher valence to Watch than to Swipe
        # create_or_retrieve_primitive(self.primitive_interactions, workspace.actions[ACTION_SWIPE], OUTCOME_FOCUS_FRONT, 1)
        # create_or_retrieve_primitive(self.primitive_interactions, workspace.actions[ACTION_FORWARD], OUTCOME_FOCUS_FRONT, 1)
        # create_or_retrieve_primitive(self.primitive_interactions, workspace.actions[ACTION_WATCH], OUTCOME_FOCUS_FRONT, 2)
        self.too_far = FOCUS_TOO_FAR_DISTANCE

        self.action = self.workspace.actions[ACTION_WATCH]

    def activation_level(self):
        """The level of activation of this decider: -1: default, 5 if focus not too far """
        activation_level = -1

        # Activate when the robot is at the center and the focus is not too far
        if TER in self.workspace.memory.phenomenon_memory.phenomena:
            if self.workspace.memory.phenomenon_memory.phenomena[TER].confidence > TERRAIN_INITIAL_CONFIDENCE + 0.01:
                if np.linalg.norm(self.workspace.memory.allocentric_memory.robot_point - self.workspace.memory.phenomenon_memory.origin_point()) < 400:
                    if self.workspace.memory.egocentric_memory.focus_point is not None:
                        if np.linalg.norm(self.workspace.memory.egocentric_memory.focus_point) < FOCUS_TOO_FAR_DISTANCE:
                            activation_level = 5

        return activation_level

    def select_enaction(self, outcome):
        """Add the next enaction to the stack based on sequence learning and spatial modifiers"""

        # If there is an object to push
        if self.workspace.memory.egocentric_memory.focus_point is not None and outcome != OUTCOME_FOCUS_TOO_FAR:
            playsound('autocat/Assets/tiny_cute.wav', False)
            # Compute the prompt
            self.workspace.memory.egocentric_memory.prompt_point = self.workspace.memory.egocentric_memory.focus_point.copy()
            # First enaction: turn to the prompt
            e0 = Enaction(self.workspace.actions[ACTION_TURN], self.workspace.memory)
            # Second enaction: move forward to the prompt
            e1 = Enaction(self.workspace.actions[ACTION_FORWARD], e0.post_memory)
            # Third enaction: move back to the origin
            origin = e1.post_memory.phenomenon_memory.origin_point()  # Birth place or arena center
            e1.post_memory.egocentric_memory.prompt_point = e1.post_memory.allocentric_to_egocentric(origin)
            print("Return to center, egocentric position", e1.post_memory.egocentric_memory.prompt_point)
            e2 = Enaction(self.workspace.actions[ACTION_BACKWARD], e1.post_memory)
            composite_enaction = CompositeEnaction([e0, e1, e2])
        else:
            # If there is no object then watch
            print("Push decider is watching")
            composite_enaction = Enaction(self.workspace.actions[ACTION_WATCH], self.workspace.memory)

        return composite_enaction
