########################################################################################
# This decider makes the robot stay in the watch point and watch for object in the center of the terrrain
# Activation 2 if emotion is SAD
########################################################################################

import math
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
        # create_or_retrieve_primitive(self.primitive_interactions, workspace.actions[ACTION_SWIPE], OUTCOME_FOCUS_FRONT, 1)
        # create_or_retrieve_primitive(self.primitive_interactions, workspace.actions[ACTION_FORWARD], OUTCOME_FOCUS_FRONT, 1)
        # create_or_retrieve_primitive(self.primitive_interactions, workspace.actions[ACTION_WATCH], OUTCOME_FOCUS_FRONT, 2)

    def activation_level(self):
        """The level of activation is 2 if the robot is SAD or UPSET"""
        if self.workspace.memory.emotion_code in [EMOTION_SAD, EMOTION_UPSET]:
            return 2
        else:
            return 0

    def select_enaction(self, enaction):
        """Return the next intended interaction"""

        ego_watch_point = self.workspace.memory.allocentric_to_egocentric(
            self.workspace.memory.phenomenon_memory.watch_point())
        ego_arrange_point = self.workspace.memory.terrain_centric_to_egocentric(
            self.workspace.memory.phenomenon_memory.arrange_point())

        e_memory = self.workspace.memory.save()
        e_memory.emotion_code = EMOTION_SAD

        # If far from watch point then go to watch point
        if np.linalg.norm(ego_watch_point) > 200:
            e_memory.egocentric_memory.prompt_point = ego_watch_point
            e_memory.egocentric_memory.focus_point = None
            # First enaction: turn to the prompt
            e0 = Enaction(self.workspace.actions[ACTION_TURN], e_memory)
            # Second enaction: move forward to the prompt
            e1 = Enaction(self.workspace.actions[ACTION_FORWARD], e0.predicted_memory.save())
            # Third enaction: scan
            e2 = Enaction(self.workspace.actions[ACTION_SCAN], e1.predicted_memory.save(), span=10)
            composite_enaction = CompositeEnaction([e0, e1, e2])  # Scan because it often miss an object

        # If facing arrange point then WATCH arrange point
        elif abs(math.atan2(ego_arrange_point[1], ego_arrange_point[0])) < 0.349:
            e_memory.egocentric_memory.prompt_point = None
            e_memory.egocentric_memory.focus_point = ego_arrange_point
            composite_enaction = Enaction(self.workspace.actions[ACTION_WATCH], e_memory)

        # If not facing arrange point then turn to arrange point
        else:
            e_memory.egocentric_memory.prompt_point = ego_arrange_point
            e_memory.egocentric_memory.focus_point = ego_arrange_point
            composite_enaction = Enaction(self.workspace.actions[ACTION_TURN], e_memory)

        # Return the selected enaction
        return composite_enaction
