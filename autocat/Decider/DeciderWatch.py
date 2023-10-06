########################################################################################
# This decider makes the robot stay in place and look at objects in its surrounding
# Activation 4: default.
########################################################################################

import math
from playsound import playsound
import numpy as np
from . Action import ACTION_WATCH, ACTION_TURN, ACTION_SWIPE, ACTION_FORWARD, ACTION_SCAN
from ..Robot.Enaction import Enaction
from ..Memory.BodyMemory import ENERGY_TIRED, EXCITATION_LOW
from ..Enaction.CompositeEnaction import CompositeEnaction
from . Decider import Decider, FOCUS_TOO_TOO_FAR_DISTANCE, FOCUS_FAR_DISTANCE
from . PredefinedInteractions import create_or_retrieve_primitive, OUTCOME_FOCUS_SIDE, OUTCOME_FOCUS_FRONT, OUTCOME_FOCUS_TOO_FAR


class DeciderWatch(Decider):
    def __init__(self, workspace):
        super().__init__(workspace)

        # Give higher valence to Watch than to Swipe
        create_or_retrieve_primitive(self.primitive_interactions, workspace.actions[ACTION_SWIPE], OUTCOME_FOCUS_FRONT, 1)
        create_or_retrieve_primitive(self.primitive_interactions, workspace.actions[ACTION_FORWARD], OUTCOME_FOCUS_FRONT, 1)
        create_or_retrieve_primitive(self.primitive_interactions, workspace.actions[ACTION_WATCH], OUTCOME_FOCUS_FRONT, 2)

        # Beyond this threshold, the robot ignores the echo and keep scanning and turning 180° in search for echos
        # self.too_far = FOCUS_TOO_TOO_FAR_DISTANCE  # Good for following another robot
        self.too_far = FOCUS_FAR_DISTANCE  # Good for active watching for new objects to push

        self.action = self.workspace.actions[ACTION_WATCH]

    def activation_level(self):
        """The level of activation is 4 if the agent is not excited and not tired"""
        if self.workspace.memory.body_memory.excitation < EXCITATION_LOW and \
                self.workspace.memory.body_memory.energy > ENERGY_TIRED:
            return 4
        else:
            return 0

    def outcome(self, enaction):
        """ Convert the enacted interaction into an outcome adapted to the watch behavior """

        outcome = super().outcome(enaction)

        # If a message was received
        if enaction is not None and enaction.message is not None:
            other_angle = math.atan2(enaction.message.ego_position[1], enaction.message.ego_position[0])
            if math.fabs(other_angle) > math.pi / 6:
                # Focus on the other robot's destination
                print("Other ego destination point", enaction.message.ego_position)
                print("Other angle", math.degrees(other_angle))
                playsound('autocat/Assets/chirp.wav', False)
                self.workspace.memory.egocentric_memory.focus_point = enaction.message.ego_position
                outcome = OUTCOME_FOCUS_SIDE

        return outcome

    def select_enaction(self, outcome):
        """Return the next intended interaction"""

        # If far from the origin then return to origin
        if np.linalg.norm(self.workspace.memory.allocentric_memory.robot_point - self.workspace.memory.phenomenon_memory.terrain_center()) > 400:
            self.workspace.memory.egocentric_memory.prompt_point = \
                self.workspace.memory.allocentric_to_egocentric(self.workspace.memory.phenomenon_memory.terrain_center())
            self.workspace.memory.egocentric_memory.focus_point = None  # Prevent unnatural head movement
            # First enaction: turn to the prompt
            e0 = Enaction(self.workspace.actions[ACTION_TURN], self.workspace.memory)
            # Second enaction: move forward to the prompt
            e1 = Enaction(self.workspace.actions[ACTION_FORWARD], e0.post_memory)
            # Third enaction: scan
            e2 = Enaction(self.workspace.actions[ACTION_SCAN], e1.post_memory, span=10)
            return CompositeEnaction([e0, e1])  # , e2])

        # Call the sequence learning mechanism to select the next action
        self.select_action(outcome)
        span = 40

        # Set the spatial modifiers
        if self.action.action_code in [ACTION_TURN]:
            if outcome == OUTCOME_FOCUS_TOO_FAR or self.workspace.memory.egocentric_memory.focus_point is None:
                # If focus TOO FAR or None then turn around
                self.workspace.memory.egocentric_memory.prompt_point = np.array([-100, 0, 0], dtype=int)
            else:
                # If focus SIDE then turn to the focus
                self.workspace.memory.egocentric_memory.prompt_point = \
                    self.workspace.memory.egocentric_memory.focus_point.copy()
        else:
            self.workspace.memory.egocentric_memory.prompt_point = None
            if self.action.action_code in [ACTION_SCAN]:
                # Watch carefully
                span = 10

        # Return the selected enaction
        return Enaction(self.action, self.workspace.memory, span=span)
