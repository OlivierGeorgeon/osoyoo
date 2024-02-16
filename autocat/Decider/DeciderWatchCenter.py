########################################################################################
# This decider makes the robot stay in the watch point and watch for object in the center of the terrrain
# Activation 2 if emotion is SAD
########################################################################################

import math
# from playsound import playsound
import numpy as np
from . Action import ACTION_WATCH, ACTION_TURN, ACTION_SWIPE, ACTION_FORWARD, ACTION_SCAN
from ..Robot.Enaction import Enaction
from ..Memory.Memory import EMOTION_SAD, EMOTION_UPSET
from ..Enaction.CompositeEnaction import CompositeEnaction
from . Decider import Decider
from . PredefinedInteractions import create_or_retrieve_primitive, OUTCOME_FOCUS_FRONT


class DeciderWatchCenter(Decider):
    def __init__(self, workspace):
        super().__init__(workspace)

        # Give higher valence to Watch than to Swipe
        create_or_retrieve_primitive(self.primitive_interactions, workspace.actions[ACTION_SWIPE], OUTCOME_FOCUS_FRONT, 1)
        create_or_retrieve_primitive(self.primitive_interactions, workspace.actions[ACTION_FORWARD], OUTCOME_FOCUS_FRONT, 1)
        create_or_retrieve_primitive(self.primitive_interactions, workspace.actions[ACTION_WATCH], OUTCOME_FOCUS_FRONT, 2)

        # Beyond this threshold, the robot ignores the echo and keep scanning and turning 180° in search for echos
        # self.too_far = FOCUS_FAR_DISTANCE  # Good for active watching for new objects to push

        self.action = self.workspace.actions[ACTION_WATCH]

    def activation_level(self):
        """The level of activation is 2 if the robot is SAD or UPSET"""
        if self.workspace.memory.emotion_code in [EMOTION_SAD, EMOTION_UPSET]:
            return 2
        else:
            return 0

    def outcome(self, enaction):
        """ Convert the enacted interaction into an outcome adapted to the watch behavior """

        outcome = super().outcome(enaction)
        return outcome

    def select_enaction(self, outcome):
        """Return the next intended interaction"""

        # If far from the origin then return to origin
        distance_to_watch_point = np.linalg.norm(self.workspace.memory.allocentric_memory.robot_point -
                                                 self.workspace.memory.phenomenon_memory.watch_point())
        print("Distance to watch point", round(distance_to_watch_point))
        if distance_to_watch_point > 200:
            self.workspace.memory.egocentric_memory.prompt_point = \
                self.workspace.memory.allocentric_to_egocentric(self.workspace.memory.phenomenon_memory.watch_point())
            self.workspace.memory.egocentric_memory.focus_point = None  # Prevent unnatural head movement
            # First enaction: turn to the prompt
            e0 = Enaction(self.workspace.actions[ACTION_TURN], self.workspace.memory)
            # Second enaction: move forward to the prompt
            e1 = Enaction(self.workspace.actions[ACTION_FORWARD], e0.predicted_memory)
            # Third enaction: scan
            e2 = Enaction(self.workspace.actions[ACTION_SCAN], e1.predicted_memory, span=10)
            return CompositeEnaction([e0, e1, e2])  # Scan because it often miss an object

        # Call the sequence learning mechanism to select the next action
        self.select_action(outcome)
        span = 40

        # Set the spatial modifiers
        if self.action.action_code in [ACTION_TURN]:
            if self.workspace.memory.egocentric_memory.focus_point is None or \
                    not self.workspace.memory.is_to_arrange(self.workspace.memory.egocentric_memory.focus_point):
                # If no focus or not in the arrange area then turn to the terrain center
                self.workspace.memory.egocentric_memory.prompt_point = \
                    self.workspace.memory.terrain_centric_to_egocentric(np.array([0, 0, 0]))
            else:
                # If focus to arrange then turn to the focus
                self.workspace.memory.egocentric_memory.prompt_point = \
                    self.workspace.memory.egocentric_memory.focus_point.copy()
        else:
            self.workspace.memory.egocentric_memory.prompt_point = None
            if self.action.action_code in [ACTION_SCAN]:
                # Watch carefully
                span = 10

        # Return the selected enaction
        return Enaction(self.action, self.workspace.memory, span=span)
